"""Step 1: read-only inventory of the gallery's data/max directory.

Run from webapp: py tools/photo-tools/media_scanner.py backend/public/data/max
Only Python's standard library is required. Indentation uses tabs.
"""

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SourceMedia:
	file: Path
	path: str
	type: str


@dataclass
class FolderScan:
	path: str
	name: str
	folders: list[str] = field(default_factory=list)
	media: list[SourceMedia] = field(default_factory=list)


@dataclass
class ScanResult:
	folders: list[FolderScan] = field(default_factory=list)
	skipped: list[tuple[str, str]] = field(default_factory=list)


class MediaScanner:
	"""Discover candidates; metadata decoding and index writing come later."""

	PHOTO_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".webp"})
	VIDEO_EXTENSIONS = frozenset({".mp4", ".m4v", ".mov", ".webm", ".mkv", ".avi"})

	def __init__(self, max_root: Path):
		self.max_root = Path(max_root).expanduser().resolve(strict=True)
		if not self.max_root.is_dir():
			raise NotADirectoryError(f"Expected a media directory: {self.max_root}")

	def scan(self) -> ScanResult:
		result = ScanResult()
		pending = [self.max_root]
		while pending:
			directory = pending.pop()
			folder = self._scan_folder(directory, result)
			result.folders.append(folder)
			pending.extend(self.max_root / path for path in reversed(folder.folders))
		return result

	def _scan_folder(self, directory: Path, result: ScanResult) -> FolderScan:
		path = self._relative_path(directory)
		folder = FolderScan(path, directory.name if path else "All photos")
		for entry in sorted(directory.iterdir(), key=self._natural_key):
			self._add_entry(entry, folder, result)
		return folder

	def _add_entry(self, entry: Path, folder: FolderScan, result: ScanResult) -> None:
		path = self._relative_path(entry)
		reason = self._skip_reason(entry)
		if reason:
			result.skipped.append((path, reason))
			return
		self._validate_name(entry.name)
		if entry.is_dir():
			folder.folders.append(path)
			return
		media_type = self._media_type(entry)
		if entry.is_file() and media_type:
			folder.media.append(SourceMedia(entry, path, media_type))
		else:
			result.skipped.append((path, "unsupported file type"))

	def _relative_path(self, path: Path) -> str:
		return "" if path == self.max_root else path.relative_to(self.max_root).as_posix()

	@staticmethod
	def _natural_key(path: Path) -> tuple:
		parts = re.split(r"([0-9]+)", path.name.casefold())
		key = tuple((1, int(part)) if part.isdigit() else (0, part) for part in parts)
		# Exact spelling breaks ties, so filesystem enumeration never decides order.
		return key, path.name

	@staticmethod
	def _skip_reason(entry: Path) -> str | None:
		if entry.name.startswith("."):
			return "dot-prefixed entry"
		if entry.is_symlink() or entry.is_junction():
			return "symbolic link or junction"
		return None

	@staticmethod
	def _validate_name(name: str) -> None:
		try:
			name.encode("utf-8")
		except UnicodeEncodeError as error:
			raise ValueError(f"Filename is not valid UTF-8: {name!r}") from error
		if any(char in "\\:" or ord(char) < 32 or ord(char) == 127 for char in name):
			raise ValueError(f"Filename is incompatible with the gallery API: {name!r}")

	@classmethod
	def _media_type(cls, path: Path) -> str | None:
		extension = path.suffix.lower()
		if extension in cls.PHOTO_EXTENSIONS:
			return "photo"
		if extension in cls.VIDEO_EXTENSIONS:
			return "video"
		return None


def print_report(result: ScanResult) -> None:
	photos = videos = 0
	for folder in result.folders:
		print(f"Folder: {folder.path or '(root)'}")
		for child in folder.folders:
			print(f"  folder  {child}")
		for item in folder.media:
			print(f"  {item.type:6}  {item.path}")
			photos += item.type == "photo"
			videos += item.type == "video"
	for path, reason in result.skipped:
		print(f"Skipped: {path} ({reason})")
	print(f"\n{len(result.folders)} folders (including root), "
		f"{photos} photos, {videos} videos, {len(result.skipped)} skipped entries.")
	print("Inventory only: file contents and browser playback have not been validated.")


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("max_root", type=Path, help="Path to backend/public/data/max")
	args = parser.parse_args()
	try:
		result = MediaScanner(args.max_root).scan()
	except (OSError, ValueError) as error:
		parser.exit(1, f"Scan failed: {error}\n")
	print_report(result)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
