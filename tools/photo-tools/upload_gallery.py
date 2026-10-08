"""Upload prepared gallery data over plain FTP, or preview locally with --dry-run."""

import argparse
import ftplib
import getpass
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from check_upload_connection import read_credentials
from ftp_client import FtpClient
from gallery_uploader import GalleryUploader
from preparation_config import PreparationConfig
from upload_config import UploadConfig
from upload_cache import UploadCache
from upload_planner import UploadPlanner
from upload_images import UploadImagePreparer


def arguments():
	base = Path(__file__).resolve().parent
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("data_root", nargs="?", type=Path, help="Override the local data directory")
	parser.add_argument("--config", type=Path, default=base / "gallery-config.json")
	parser.add_argument("--upload-config", type=Path, default=base / "upload-config.json")
	parser.add_argument("--dry-run", action="store_true", help="List planned files without connecting")
	parser.add_argument("--force", action="store_true", help="Upload every planned file, ignoring upload receipts")
	return parser.parse_args()


def run(args) -> None:
	preparation = PreparationConfig.from_arguments(args)
	connection = UploadConfig.load(args.upload_config)
	plan = UploadPlanner(preparation.data_root).build()
	with TemporaryDirectory(prefix="gallery-upload-") as staging:
		plan = UploadImagePreparer(Path(staging), connection.photo_max_edge,
			connection.photo_quality).prepare(plan)
		_run_plan(args, preparation, connection, plan)


def _run_plan(args, preparation, connection, plan) -> None:
	print(f"Local data directory: {preparation.data_root}")
	print(f"FTP destination: {connection.host}:{connection.port} / {connection.remote_data_dir}")
	print(f"Upload plan: {len(plan.items)} files; {plan.total_bytes:,} bytes.")
	if args.dry_run:
		for item in plan.items:
			print(f"{item.kind:9} {item.relative_path} ({item.size:,} bytes)")
		print("Local inventory only; actual skips require a connection and remote metadata checks.")
		print("Dry run complete. No connection or remote changes were made.")
		return
	print("Full upload requested." if args.force else "Incremental upload: checking content and remote metadata.", flush=True)
	with FtpClient(connection) as client:
		username, password = read_credentials(connection)
		try:
			client.login(username, password)
		finally:
			password = None
		print(f"Login directory: {client.working_directory()}")
		remote_dir = client.enter_data_directory()
		print(f"Server data directory: {remote_dir}", flush=True)
		cache = UploadCache({
			"protocol": connection.protocol, "host": connection.host.lower(),
			"port": connection.port, "username": username, "remote_data_dir": remote_dir,
			"local_data_dir": str(preparation.data_root.resolve())
		})
		uploader = GalleryUploader(client, cache, force=args.force)
		count = uploader.upload(plan)
	print(f"Upload completed: {count} uploaded, {uploader.skipped} skipped. No old gallery files were deleted.")


def main() -> int:
	args = arguments()
	try:
		run(args)
	except getpass.GetPassWarning:
		print("Cannot hide password input here. Use a normal Windows terminal or the launcher.", file=sys.stderr)
		return 1
	except (KeyboardInterrupt, EOFError):
		print("\nUpload cancelled or connection/input ended. Rerun to retry.", file=sys.stderr)
		return 1
	except (OSError, ftplib.Error, ValueError, TypeError, KeyError, OverflowError, RuntimeError) as error:
		print(f"Upload failed: {error}", file=sys.stderr)
		return 1
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
