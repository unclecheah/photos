"""Local metadata cache for the combined gallery preparation command."""

import hashlib
import json
import math
import os
import sys
import tempfile
from dataclasses import asdict
from pathlib import Path

import PIL

from media_scanner import SourceMedia
from photo_processor import PhotoResult
from video_processor import VideoResult


class PreparationCache:

	VERSION = 1

	def __init__(self, data_root: Path, image_options: dict, video_options: dict):
		self.data_root = Path(data_root).resolve(strict=True)
		self.thumbnail_root = (self.data_root / "thumbnail").resolve()
		self.identity = os.path.normcase(str(self.data_root))
		key = hashlib.sha256(self.identity.encode("utf-8")).hexdigest()[:16]
		self.file = Path(__file__).resolve().parent / ".cache" / f"gallery-{key}.json"
		self.settings = self._settings(image_options, video_options)
		self.entries = self._load()

	@staticmethod
	def _settings(image_options: dict, video_options: dict) -> dict:
		common = {**image_options, "pillow_version": PIL.__version__}
		settings = {}
		for media_type in ("photo", "video"):
			module = Path(__file__).with_name(f"{media_type}_processor.py")
			settings[media_type] = {**common,
				"processor_sha256": hashlib.sha256(module.read_bytes()).hexdigest()}
		settings["video"].update({name: video_options.get(name) for name in ("ffmpeg", "ffprobe")})
		return settings

	def _load(self) -> dict:
		try:
			with self.file.open(encoding="utf-8") as handle:
				data = json.load(handle)
			if not isinstance(data, dict):
				raise ValueError("Expected a cache object")
			if data.get("version") != self.VERSION or data.get("data_root") != self.identity:
				return {}
			entries = data.get("entries")
			if not isinstance(entries, dict):
				raise ValueError("Expected cache entries")
			return entries
		except FileNotFoundError:
			return {}
		except (OSError, ValueError) as error:
			print(f"Cache ignored; media will be regenerated: {error}", file=sys.stderr)
			return {}

	@staticmethod
	def signature(file: Path) -> dict:
		stat = file.stat()
		if not file.is_file():
			raise ValueError(f"Expected a file: {file}")
		return {"size": stat.st_size, "mtime_ns": stat.st_mtime_ns}

	def get(self, source: SourceMedia, source_signature: dict) -> PhotoResult | VideoResult | None:
		try:
			entry = self.entries.get(source.path)
			if not isinstance(entry, dict) or entry.get("type") != source.type:
				return None
			if entry.get("settings") != self.settings[source.type]:
				return None
			if entry.get("source_signature") != source_signature:
				return None
			thumbnail = self._thumbnail_file(source)
			if entry.get("thumbnail_signature") != self.signature(thumbnail):
				return None
			return self._restore(source, entry["result"], thumbnail)
		except (OSError, ValueError, KeyError, TypeError, OverflowError):
			# Missing thumbnails and malformed individual records are cache misses.
			return None

	def _thumbnail_file(self, source: SourceMedia) -> Path:
		thumbnail = self.thumbnail_root / Path(*source.path.split("/"))
		thumbnail = thumbnail.with_name(thumbnail.name + ".jpg")
		if thumbnail.is_symlink() or not thumbnail.resolve().is_relative_to(self.thumbnail_root):
			raise ValueError("Cached thumbnail is outside its expected output directory")
		return thumbnail

	@staticmethod
	def _restore(source: SourceMedia, metadata: dict, thumbnail: Path) -> PhotoResult | VideoResult:
		if not isinstance(metadata, dict):
			raise ValueError("Invalid cached metadata")
		values = dict(metadata)
		if values.get("path") != source.path or values.get("thumbnail_path") != source.path + ".jpg":
			raise ValueError("Cached paths do not match the source")
		for key in ("width", "height", "thumbnail_width", "thumbnail_height"):
			if type(values.get(key)) is not int or values[key] <= 0:
				raise ValueError("Invalid cached dimensions")
		values["thumbnail_file"] = thumbnail
		if source.type == "photo":
			return PhotoResult(**values)
		PreparationCache._validate_video(values)
		return VideoResult(**values)

	@staticmethod
	def _validate_video(values: dict) -> None:
		for key in ("duration_seconds", "poster_seconds"):
			value = values[key]
			if key == "duration_seconds" and value is None:
				continue
			if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
				raise ValueError("Invalid cached video timing")
		if values["duration"] is not None and not isinstance(values["duration"], str):
			raise ValueError("Invalid cached duration label")
		if not isinstance(values["codec"], str):
			raise ValueError("Invalid cached codec")

	def remember(self, source: SourceMedia, result: PhotoResult | VideoResult, before: dict) -> None:
		self.check_source(source, before)
		thumbnail = self._thumbnail_file(source)
		if Path(result.thumbnail_file).resolve(strict=True) != thumbnail.resolve(strict=True):
			raise ValueError("Prepared thumbnail path does not match the cache path")
		metadata = asdict(result)
		metadata.pop("thumbnail_file")
		self._restore(source, metadata, thumbnail)
		self.entries[source.path] = {
			"type": source.type,
			"settings": self.settings[source.type],
			"source_signature": before,
			"thumbnail_signature": self.signature(thumbnail),
			"result": metadata
		}

	def check_source(self, source: SourceMedia, before: dict) -> None:
		if self.signature(source.file) != before:
			raise ValueError(f"Source changed during preparation: {source.path}; rerun when copying/editing finishes")

	def forget(self, path: str) -> None:
		self.entries.pop(path, None)

	def retain(self, paths: set[str]) -> None:
		self.entries = {path: entry for path, entry in self.entries.items() if path in paths}

	def save(self) -> None:
		self.file.parent.mkdir(parents=True, exist_ok=True)
		temporary = None
		data = {"version": self.VERSION, "data_root": self.identity, "entries": self.entries}
		try:
			with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
				dir=self.file.parent, prefix=".cache-", suffix=".tmp", delete=False) as handle:
				temporary = Path(handle.name)
				json.dump(data, handle, ensure_ascii=False, indent="\t", allow_nan=False)
				handle.write("\n")
			temporary.replace(self.file)
		finally:
			if temporary is not None:
				temporary.unlink(missing_ok=True)
