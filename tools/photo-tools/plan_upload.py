"""Show a local upload inventory. This command never connects to a server."""

import argparse
import sys
from pathlib import Path

from preparation_config import PreparationConfig
from upload_planner import UploadPlanner


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("data_root", nargs="?", type=Path, help="Local data directory")
	parser.add_argument("--config", type=Path, help="Existing gallery-config.json")
	args = parser.parse_args()
	try:
		config = PreparationConfig.from_arguments(args)
		plan = UploadPlanner(config.data_root).build()
	except (OSError, ValueError, TypeError, KeyError, OverflowError) as error:
		print(f"Upload planning failed: {error}", file=sys.stderr)
		return 1
	print(f"Local data directory: {config.data_root}")
	for item in plan.items:
		print(f"{item.kind:9} {item.relative_path} ({item.size:,} bytes)")
	counts = {kind: sum(item.kind == kind for item in plan.items)
		for kind in ("original", "thumbnail", "index")}
	print(f"\n{counts['original']} originals, {counts['thumbnail']} thumbnails, "
		f"{counts['index']} indexes; {len(plan.items)} files; {plan.total_bytes:,} bytes.")
	print("These paths are relative to the future remote data directory.")
	print("No connection, transfer, deletion or remote comparison was performed.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
