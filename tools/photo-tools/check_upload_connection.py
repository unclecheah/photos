"""Check FTP login and remote directory listing. No remote files are modified."""

import argparse
import ftplib
import getpass
import sys
import warnings
from pathlib import Path

from ftp_client import FtpClient
from upload_config import UploadConfig


def read_credentials(config: UploadConfig) -> tuple[str, str]:
	prompt = f"Username [{config.username}]: " if config.username else "Username: "
	username = input(prompt).strip() or config.username
	if not username:
		raise ValueError("A username is required")
	with warnings.catch_warnings():
		warnings.simplefilter("error", getpass.GetPassWarning)
		password = getpass.getpass("Upload password: ")
	return username, password


def check_connection(config: UploadConfig) -> None:
	print(f"Connecting to {config.host}:{config.port} using plain FTP...", flush=True)
	with FtpClient(config) as client:
		print("Connected. Enter credentials locally.")
		username, password = read_credentials(config)
		try:
			client.login(username, password)
		finally:
			password = None  # No password is saved to configuration or session attributes.
		print(f"Login succeeded. Login directory: {client.working_directory()}")
		print(f"Opening remote data directory: {config.remote_data_dir}", flush=True)
		print(f"Server reports data directory: {client.enter_data_directory()}")
		names = sorted(client.list_names(), key=lambda name: (name.casefold(), name))
		print(f"Directory listing succeeded: {len(names)} entries.")
		for name in names[:20]:
			print(f"  {name!r}")
		if len(names) > 20:
			print(f"  ... {len(names) - 20} more entries")
	print("Connection check completed. No files were uploaded, created, renamed or deleted.")


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--config", type=Path,
		default=Path(__file__).resolve().with_name("upload-config.json"))
	args = parser.parse_args()
	try:
		check_connection(UploadConfig.load(args.config))
	except getpass.GetPassWarning:
		print("Cannot hide password input here. Run from a normal Windows terminal or the launcher.", file=sys.stderr)
		return 1
	except (KeyboardInterrupt, EOFError):
		print("\nConnection check cancelled or the connection/input ended.", file=sys.stderr)
		return 1
	except (OSError, ftplib.Error, ValueError, TypeError, OverflowError) as error:
		print(f"Connection check failed: {error}", file=sys.stderr)
		return 1
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
