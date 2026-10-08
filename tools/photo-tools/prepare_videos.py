"""Prepare video stills. Run from the directory containing tools/ and webapp/."""

import argparse
import sys
from pathlib import Path

from media_scanner import MediaScanner, ScanResult
from video_processor import VideoProcessor, VideoProcessingError


def prepare_videos(scan: ScanResult, processor: VideoProcessor) -> int:
	prepared = failed = photos = 0
	for folder in scan.folders:
		for source in folder.media:
			if source.type == "photo":
				photos += 1
				continue
			try:
				result = processor.prepare(source)
				prepared += 1
				print(f"Prepared: {result.path} ({result.width} x {result.height}, "
					f"{result.duration or 'unknown duration'}, codec={result.codec}) -> "
					f"{result.thumbnail_path} ({result.thumbnail_width} x {result.thumbnail_height}, "
					f"frame requested at {result.poster_seconds:.3f}s)")
			except (VideoProcessingError, OSError, ValueError, KeyError, TypeError) as error:
				failed += 1
				print(f"Failed: {source.path}: {error}", file=sys.stderr)
	for path, reason in scan.skipped:
		print(f"Skipped: {path} ({reason})")
	print(f"\nPrepared {prepared} videos; failed {failed}; "
		f"left {photos} photos to the photo tool; skipped {len(scan.skipped)} entries.")
	print("Indexes are unchanged. Stills are regenerated each run; browser playback is not verified.")
	return 1 if failed else 0


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("max_root", type=Path, help="Path to webapp/backend/public/data/max")
	parser.add_argument("--thumbnail-root", type=Path, help="Default: thumbnail beside max")
	parser.add_argument("--max-edge", type=int, default=640)
	parser.add_argument("--quality", type=int, default=85)
	parser.add_argument("--ffmpeg", help="Optional path to ffmpeg.exe")
	parser.add_argument("--ffprobe", help="Optional path to ffprobe.exe")
	parser.add_argument("--timeout", type=float, default=60, help="Seconds per external command")
	args = parser.parse_args()
	try:
		scanner = MediaScanner(args.max_root)
		thumbnail_root = args.thumbnail_root or scanner.max_root.parent / "thumbnail"
		processor = VideoProcessor(scanner.max_root, thumbnail_root,
			max_edge=args.max_edge, quality=args.quality, ffmpeg=args.ffmpeg,
			ffprobe=args.ffprobe, timeout=args.timeout)
		scan = scanner.scan()
	except (VideoProcessingError, OSError, ValueError) as error:
		parser.exit(1, f"Preparation failed: {error}\n")
	print(f"Source: {scanner.max_root}\nThumbnails: {processor.thumbnail_root}")
	return prepare_videos(scan, processor)


if __name__ == "__main__":
	raise SystemExit(main())
