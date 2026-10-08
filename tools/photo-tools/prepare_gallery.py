"""Prepare photos/videos and write version-1 indexes. No upload or cleanup."""

import argparse
import math
import sys
from pathlib import Path

from PIL import Image

from index_writer import IndexWriter
from media_scanner import MediaScanner, ScanResult
from photo_processor import PhotoProcessor
from preparation_cache import PreparationCache
from preparation_config import PreparationConfig
from video_processor import VideoProcessor, VideoProcessingError


class GalleryPreparationError(Exception):
	pass


class GalleryPreparer:

	def __init__(self, data_root: Path, *, max_edge=640, quality=85, root_name="All photos",
		ffmpeg=None, ffprobe=None, timeout=60, force=False):
		self._validate_options(max_edge, quality, timeout)
		self.writer = IndexWriter(data_root, root_name=root_name)
		self.scanner = MediaScanner(self.writer.max_root)
		self.image_options = {"max_edge": max_edge, "quality": quality}
		self.video_options = {"ffmpeg": ffmpeg, "ffprobe": ffprobe, "timeout": timeout}
		self.cache = PreparationCache(self.writer.data_root, self.image_options, self.video_options)
		self.force = force
		self.processors = {}
		self.prepared = self.reused = 0

	@staticmethod
	def _validate_options(max_edge: int, quality: int, timeout: float) -> None:
		if type(max_edge) is not int or not 1 <= max_edge <= 8192:
			raise ValueError("max_edge must be an integer between 1 and 8192")
		if type(quality) is not int or not 1 <= quality <= 95:
			raise ValueError("quality must be an integer between 1 and 95")
		if not math.isfinite(timeout) or timeout <= 0:
			raise ValueError("timeout must be a positive number")

	def prepare(self) -> None:
		self.prepared = self.reused = 0
		scan = self.scanner.scan()
		self.cache.retain({source.path for folder in scan.folders for source in folder.media})
		for path, reason in scan.skipped:
			print(f"Skipped: {path} ({reason})")
		results = self._prepare_media(scan)
		# Build everything in memory; missing results/files prevent index writes.
		indexes = self.writer.build(scan, results)
		count = self.writer.write(indexes)
		print(f"\nPrepared {self.prepared}; reused {self.reused}; wrote {count} folder indexes; "
			f"skipped {len(scan.skipped)} entries.")
		print(f"Indexes: {self.writer.index_root}")
		print(f"Cache: {self.cache.file}")
		print("No upload or media-file cleanup was performed. Use --force to rebuild all media.")

	def _processor(self, media_type: str):
		if media_type not in self.processors:
			arguments = (self.writer.max_root, self.writer.thumbnail_root)
			if media_type == "photo":
				self.processors[media_type] = PhotoProcessor(*arguments, **self.image_options)
			else:
				self.processors[media_type] = VideoProcessor(*arguments, **self.image_options, **self.video_options)
		return self.processors[media_type]

	def _prepare_media(self, scan: ScanResult) -> dict:
		results = {}
		failed = 0
		for folder in scan.folders:
			for source in folder.media:
				try:
					results[source.path] = self._prepare_one(source)
				except (VideoProcessingError, OSError, ValueError, KeyError, TypeError,
					Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
					failed += 1
					self.cache.forget(source.path)
					print(f"Failed: {source.path}: {error}", file=sys.stderr)
		self._save_cache()
		if failed:
			raise GalleryPreparationError(f"Prepared {self.prepared}; reused {self.reused}; failed {failed}. "
				"No indexes were written. Fix the failures and rerun.")
		return results

	def _prepare_one(self, source):
		before = self.cache.signature(source.file)
		result = None if self.force else self.cache.get(source, before)
		if result is not None:
			self.cache.check_source(source, before)
			self.reused += 1
			print(f"Reused {source.type}: {source.path}")
			return result
		self.cache.forget(source.path)
		result = self._processor(source.type).prepare(source)
		self.cache.remember(source, result, before)
		self.prepared += 1
		print(f"Prepared {source.type}: {source.path} ({result.width} x {result.height})")
		return result

	def _save_cache(self) -> None:
		try:
			self.cache.save()
		except (OSError, ValueError) as error:
			print(f"Cache could not be saved; future runs may repeat preparation: {error}", file=sys.stderr)


def parse_arguments():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("data_root", type=Path, nargs="?", help="Data directory; optional when supplied by --config")
	parser.add_argument("--config", type=Path, help="Preparation settings JSON file")
	parser.add_argument("--max-edge", type=int, help="Override maximum thumbnail edge")
	parser.add_argument("--quality", type=int, help="Override JPEG quality")
	parser.add_argument("--root-name", help="Override root gallery title")
	parser.add_argument("--ffmpeg", help="Optional path to ffmpeg.exe")
	parser.add_argument("--ffprobe", help="Optional path to ffprobe.exe")
	parser.add_argument("--timeout", type=float, help="Override seconds allowed per external command")
	parser.add_argument("--force", action="store_true", help="Ignore cached results and regenerate every media file")
	return parser.parse_args()


def main() -> int:
	args = parse_arguments()
	try:
		config = PreparationConfig.from_arguments(args)
		print(f"Data directory: {config.data_root}")
		print(f"Thumbnail settings: edge={config.max_edge}, quality={config.quality}")
		GalleryPreparer(config.data_root, max_edge=config.max_edge, quality=config.quality,
			root_name=config.root_name, ffmpeg=config.ffmpeg, ffprobe=config.ffprobe,
			timeout=config.timeout, force=args.force).prepare()
	except (GalleryPreparationError, VideoProcessingError, OSError, ValueError, KeyError) as error:
		print(f"Preparation failed: {error}", file=sys.stderr)
		return 1
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
