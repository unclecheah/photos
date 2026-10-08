"""Prepare photo thumbnails. Run from webapp; no indexes or uploads yet."""

import argparse
import sys
from pathlib import Path

from PIL import Image

from media_scanner import MediaScanner, ScanResult
from photo_processor import PhotoProcessor


def prepare_photos(scan: ScanResult, processor: PhotoProcessor) -> int:
	prepared = failed = deferred = 0
	for folder in scan.folders:
		for source in folder.media:
			if source.type == "video":
				deferred += 1
				continue
			try:
				result = processor.prepare(source)
				prepared += 1
				print(f"Prepared: {result.path} ({result.width} x {result.height}) -> "
					f"{result.thumbnail_path} ({result.thumbnail_width} x {result.thumbnail_height})")
			except (OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
				failed += 1
				print(f"Failed: {source.path}: {error}", file=sys.stderr)
	for path, reason in scan.skipped:
		print(f"Skipped: {path} ({reason})")
	print(f"\nPrepared {prepared} photos; failed {failed}; "
		f"deferred {deferred} videos; skipped {len(scan.skipped)} entries.")
	print("Indexes are unchanged. This step regenerates every photo thumbnail on each run.")
	return 1 if failed else 0


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("max_root", type=Path, help="Path to backend/public/data/max")
	parser.add_argument("--thumbnail-root", type=Path, help="Default: thumbnail beside max")
	parser.add_argument("--max-edge", type=int, default=640, help="Longest edge in pixels (default: 640)")
	parser.add_argument("--quality", type=int, default=85, help="JPEG quality 1-95 (default: 85)")
	args = parser.parse_args()
	try:
		scanner = MediaScanner(args.max_root)
		thumbnail_root = args.thumbnail_root or scanner.max_root.parent / "thumbnail"
		processor = PhotoProcessor(scanner.max_root, thumbnail_root,
			max_edge=args.max_edge, quality=args.quality)
		scan = scanner.scan()
	except (OSError, ValueError) as error:
		parser.exit(1, f"Preparation failed: {error}\n")
	print(f"Source: {scanner.max_root}\nThumbnails: {processor.thumbnail_root}")
	return prepare_photos(scan, processor)


if __name__ == "__main__":
	raise SystemExit(main())
