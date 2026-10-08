"""Build a local upload inventory from the current reachable gallery indexes."""

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit


@dataclass(frozen=True)
class UploadItem:
	local_file: Path
	relative_path: str
	kind: str
	size: int
	mtime_ns: int

	def check_unchanged(self) -> None:
		stat = self.local_file.stat()
		if not self.local_file.is_file() or (stat.st_size, stat.st_mtime_ns) != (self.size, self.mtime_ns):
			raise ValueError(f"File changed while planning: {self.relative_path}; prepare and plan again")


@dataclass(frozen=True)
class UploadPlan:
	items: tuple[UploadItem, ...]

	@property
	def total_bytes(self) -> int:
		return sum(item.size for item in self.items)


class UploadPlanner:

	def __init__(self, data_root: Path):
		self.data_root = Path(data_root).resolve(strict=True)
		if not self.data_root.is_dir():
			raise NotADirectoryError(self.data_root)
		self.files = {}

	def build(self) -> UploadPlan:
		self.files = {}
		pending, visited = [""], set()
		while pending:
			folder = pending.pop()
			if folder in visited:
				raise ValueError(f"Repeated folder reference: {folder!r}")
			visited.add(folder)
			index = self._read_index(folder)
			self._add_media(folder, index["media"])
			pending.extend(self._child_paths(folder, index["folders"]))
		items = tuple(sorted(self.files.values(), key=self._order))
		for item in items:
			item.check_unchanged()
		return UploadPlan(items)

	def _read_index(self, folder: str) -> dict:
		relative = f"index/{folder}/index.json" if folder else "index/index.json"
		item = self._add_file(relative, "index")
		with item.local_file.open(encoding="utf-8") as handle:
			index = json.load(handle)
		item.check_unchanged()
		if not isinstance(index, dict) or type(index.get("version")) is not int or index["version"] != 1:
			raise ValueError(f"Invalid version-1 index: {relative}")
		if not isinstance(index.get("name"), str):
			raise ValueError(f"Missing folder name: {relative}")
		if not isinstance(index.get("folders"), list) or not isinstance(index.get("media"), list):
			raise ValueError(f"Invalid folder/media arrays: {relative}")
		return index

	def _add_media(self, folder: str, media: list) -> None:
		seen = set()
		for entry in media:
			if not isinstance(entry, dict) or entry.get("type") not in {"photo", "video"}:
				raise ValueError(f"Invalid media entry in {folder or '(root)'}")
			if not isinstance(entry.get("name"), str):
				raise ValueError("Media entry is missing its name")
			self._validate_dimensions(entry)
			source = self._url_path(entry.get("src"), "max")
			media_path = source[len("max/"):]
			if entry.get("id") != media_path or self._parent(media_path) != folder:
				raise ValueError(f"Media ID or folder does not match source URL: {source}")
			if media_path in seen:
				raise ValueError(f"Repeated media entry: {media_path}")
			seen.add(media_path)
			self._add_file(source, "original")
			self._add_file(self._url_path(entry.get("thumbnail"), "thumbnail"), "thumbnail")

	def _child_paths(self, parent: str, folders: list) -> list[str]:
		paths = []
		for entry in folders:
			if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
				raise ValueError(f"Invalid child entry in {parent or '(root)'}")
			path = entry.get("path")
			self._validate_relative(path)
			if self._parent(path) != parent:
				raise ValueError(f"Folder {path!r} is not an immediate child of {parent!r}")
			cover = entry.get("cover")
			if cover is not None:
				self._add_file(self._url_path(cover, "thumbnail"), "thumbnail")
			paths.append(path)
		return paths

	@staticmethod
	def _validate_dimensions(entry: dict) -> None:
		for name in ("width", "height"):
			value = entry.get(name)
			if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
				raise ValueError(f"Invalid media dimension: {name}")

	@staticmethod
	def _parent(relative: str) -> str:
		parent = PurePosixPath(relative).parent.as_posix()
		return "" if parent == "." else parent

	@staticmethod
	def _validate_relative(relative: str) -> None:
		if not isinstance(relative, str) or not relative:
			raise ValueError("Expected a non-empty relative file/folder path")
		if any(char in "\\:" or ord(char) < 32 or ord(char) == 127 for char in relative):
			raise ValueError(f"Invalid relative path: {relative!r}")
		if any(part in {"", ".", ".."} for part in relative.split("/")):
			raise ValueError(f"Invalid relative path: {relative!r}")

	def _url_path(self, url: str, branch: str) -> str:
		if not isinstance(url, str) or re.search(r"%(?![0-9a-fA-F]{2})", url):
			raise ValueError(f"Invalid media URL: {url!r}")
		parts = urlsplit(url)
		if parts.scheme or parts.netloc or parts.query or parts.fragment:
			raise ValueError(f"Expected a local /data/{branch}/ URL: {url}")
		if not parts.path.startswith(f"/data/{branch}/"):
			raise ValueError(f"Expected a /data/{branch}/ URL: {url}")
		relative = unquote(parts.path[len("/data/"):], encoding="utf-8", errors="strict")
		self._validate_relative(relative)
		return relative

	def _add_file(self, relative: str, kind: str) -> UploadItem:
		self._validate_relative(relative)
		file = (self.data_root / Path(*relative.split("/"))).resolve(strict=True)
		if not file.is_relative_to(self.data_root) or not file.is_file():
			raise ValueError(f"Referenced file is outside the data directory: {relative}")
		if relative in self.files:
			item = self.files[relative]
			item.check_unchanged()
			return item
		stat = file.stat()
		item = UploadItem(file, relative, kind, stat.st_size, stat.st_mtime_ns)
		self.files[relative] = item
		return item

	@staticmethod
	def _order(item: UploadItem) -> tuple:
		phase = {"original": 0, "thumbnail": 1, "index": 2}[item.kind]
		depth = -len(PurePosixPath(item.relative_path).parts) if item.kind == "index" else 0
		return phase, depth, item.relative_path.casefold(), item.relative_path
