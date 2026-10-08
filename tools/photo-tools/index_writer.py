"""Build and write the existing version-1 per-folder gallery indexes."""

import json
import tempfile
from pathlib import Path, PurePosixPath
from urllib.parse import quote

from media_scanner import ScanResult, SourceMedia
from photo_processor import PhotoResult
from video_processor import VideoResult


class IndexWriter:

	def __init__(self, data_root: Path, *, root_name="All photos"):
		self.data_root = Path(data_root).resolve(strict=True)
		self.max_root = (self.data_root / "max").resolve(strict=True)
		self.thumbnail_root = (self.data_root / "thumbnail").resolve()
		self.index_root = (self.data_root / "index").resolve()
		self.root_name = root_name
		self._validate_roots()

	def _validate_roots(self) -> None:
		if not self.max_root.is_dir():
			raise NotADirectoryError(self.max_root)
		roots = [self.max_root, self.thumbnail_root, self.index_root]
		for index, root in enumerate(roots):
			if root.exists() and not root.is_dir():
				raise NotADirectoryError(root)
			for other in roots[index + 1:]:
				if root.is_relative_to(other) or other.is_relative_to(root):
					raise ValueError("max, thumbnail and index must be separate directory trees")

	def build(self, scan: ScanResult, results: dict[str, PhotoResult | VideoResult]) -> dict:
		indexes = {}
		for folder in scan.folders:
			if any(part.casefold() == "index.json" for part in folder.path.split("/")):
				raise ValueError(f"Folder {folder.path!r} conflicts with the reserved index.json filename")
			indexes[folder.path] = {
				"version": 1,
				"name": folder.name if folder.path else self.root_name,
				"folders": [],
				"media": [self._media_entry(source, results[source.path]) for source in folder.media]
			}
		self._add_folders(scan, indexes)
		return indexes

	def _media_entry(self, source: SourceMedia, result: PhotoResult | VideoResult) -> dict:
		if result.path != source.path:
			raise ValueError(f"Prepared result does not match {source.path}")
		if source.type == "photo" and not isinstance(result, PhotoResult):
			raise ValueError(f"Expected photo metadata for {source.path}")
		if source.type == "video" and not isinstance(result, VideoResult):
			raise ValueError(f"Expected video metadata for {source.path}")
		self._check_file(self.max_root, source.path, source.file)
		self._check_file(self.thumbnail_root, result.thumbnail_path, result.thumbnail_file)
		if any(type(value) is not int or value <= 0 for value in (result.width, result.height)):
			raise ValueError(f"Invalid display dimensions for {source.path}")
		return {
			"id": source.path,
			"name": PurePosixPath(source.path).stem,
			"type": source.type,
			"src": self._url("max", source.path),
			"thumbnail": self._url("thumbnail", result.thumbnail_path),
			"width": result.width,
			"height": result.height,
			"duration": result.duration if isinstance(result, VideoResult) else None
		}

	def _add_folders(self, scan: ScanResult, indexes: dict) -> None:
		covers = {}
		# Scanner order is parent-first; reverse it so child covers exist first.
		for folder in reversed(scan.folders):
			index = indexes[folder.path]
			index["folders"] = [self._folder_entry(path, indexes, covers) for path in folder.folders]
			covers[folder.path] = self._cover(index)

	@staticmethod
	def _folder_entry(path: str, indexes: dict, covers: dict) -> dict:
		child = indexes[path]
		return {
			"path": path,
			"name": child["name"],
			"itemCount": len(child["media"]),
			"cover": covers[path]
		}

	@staticmethod
	def _cover(index: dict) -> str | None:
		if index["media"]:
			return index["media"][0]["thumbnail"]
		return next((child["cover"] for child in index["folders"] if child["cover"]), None)

	@staticmethod
	def _url(branch: str, relative: str) -> str:
		return f"/data/{branch}/{quote(relative, safe='/')}"

	@staticmethod
	def _relative_path(value: str, *, allow_root=False) -> Path:
		if allow_root and value == "":
			return Path()
		if not value or "\\" in value or ":" in value:
			raise ValueError(f"Invalid gallery path: {value!r}")
		parts = value.split("/")
		if any(part in {"", ".", ".."} for part in parts):
			raise ValueError(f"Invalid gallery path: {value!r}")
		return Path(*parts)

	def _check_file(self, root: Path, relative: str, reported_file: Path) -> None:
		file = (root / self._relative_path(relative)).resolve(strict=True)
		if not file.is_relative_to(root) or not file.is_file():
			raise ValueError(f"Media file is outside its expected directory: {relative}")
		if file != Path(reported_file).resolve(strict=True):
			raise ValueError(f"Prepared file does not match its relative path: {relative}")

	def _index_file(self, path: str) -> Path:
		file = self.index_root / self._relative_path(path, allow_root=True) / "index.json"
		if not file.resolve().is_relative_to(self.index_root) or file.is_symlink():
			raise ValueError(f"Invalid index destination: {path!r}")
		if file.exists() and not file.is_file():
			raise ValueError(f"Index destination is not a file: {file}")
		return file

	def write(self, indexes: dict) -> int:
		# Stage every JSON file before replacing any existing index.
		staged = []
		written = 0
		try:
			for path, index in indexes.items():
				destination = self._index_file(path)
				staged.append((self._stage(index, destination), destination))
			# Deepest folders first; root last. Each replacement is atomic, not the batch.
			for temporary, destination in sorted(staged, key=lambda pair: len(pair[1].parts), reverse=True):
				temporary.replace(destination)
				written += 1
		except (OSError, ValueError) as error:
			raise OSError(f"Index write stopped after {written} of {len(indexes)} replacements: {error}") from error
		finally:
			for temporary, _ in staged:
				temporary.unlink(missing_ok=True)
		return written

	@staticmethod
	def _stage(index: dict, destination: Path) -> Path:
		destination.parent.mkdir(parents=True, exist_ok=True)
		temporary = None
		try:
			with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
				dir=destination.parent, prefix=".index-", suffix=".tmp", delete=False) as handle:
				temporary = Path(handle.name)
				json.dump(index, handle, ensure_ascii=False, indent="\t", allow_nan=False)
				handle.write("\n")
			return temporary
		except BaseException:
			if temporary is not None:
				temporary.unlink(missing_ok=True)
			raise
