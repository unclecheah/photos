"""Plain FTP session with directory checks and staged binary uploads."""

import ftplib
import re
from pathlib import Path
from uuid import uuid4

from upload_config import UploadConfig


class FtpClient:

	def __init__(self, config: UploadConfig):
		self.config = config
		self._ftp = None
		self._data_dir = None
		self._metadata_warning = False

	def __enter__(self):
		ftp = ftplib.FTP(timeout=self.config.timeout, encoding="utf-8")
		try:
			ftp.connect(self.config.host, self.config.port)
		except BaseException:
			ftp.close()
			raise
		self._ftp = ftp
		return self

	def login(self, username: str, password: str) -> None:
		if not username or any(char in "\r\n" for char in username + password):
			raise ValueError("A username is required; credentials cannot contain line breaks")
		ftp = self._connection()
		ftp.login(user=username, passwd=password)
		ftp.set_pasv(True)

	def working_directory(self) -> str:
		return self._connection().pwd()

	def enter_data_directory(self) -> str:
		ftp = self._connection()
		ftp.cwd(self.config.remote_data_dir)
		self._data_dir = ftp.pwd()
		return self._data_dir

	def list_names(self) -> list[str]:
		return self._connection().nlst()

	def stage_file(self, local_file: Path, relative_path: str, callback=None) -> tuple[str, str]:
		"""Upload beside the destination; return temporary and final absolute paths."""
		parts = self._path_parts(relative_path)
		self._enter_parent(parts[:-1])
		ftp = self._connection()
		parent = ftp.pwd().rstrip("/")
		temporary = f"{parent}/.gallery-upload-{uuid4().hex}.part"
		destination = f"{parent}/{parts[-1]}"
		try:
			with Path(local_file).open("rb") as handle:
				ftp.storbinary("STOR " + temporary, handle, blocksize=256 * 1024, callback=callback)
		except BaseException:
			print(f"Transfer interrupted; a temporary file may remain: {temporary}", flush=True)
			# A failed data transfer may leave pending control replies. Do not reuse it.
			ftp.close()
			self._ftp = None
			raise
		return temporary, destination

	def remote_size(self, path: str) -> int:
		ftp = self._connection()
		ftp.voidcmd("TYPE I")
		size = ftp.size(path)
		if size is None:
			raise RuntimeError("Server did not return a file size; temporary file was not published")
		return size

	def publish_file(self, temporary: str, destination: str) -> None:
		# Never delete the destination as a fallback if rename is refused.
		self._connection().rename(temporary, destination)

	def file_signature(self, relative_path: str) -> dict | None:
		"""Read size and server modification time; unavailable metadata never permits a skip."""
		parts = self._path_parts(relative_path)
		if self._data_dir is None:
			raise RuntimeError("Enter the configured data directory before checking files")
		path = self._data_dir.rstrip("/") + "/" + "/".join(parts)
		try:
			size = self.remote_size(path)
			reply = self._connection().sendcmd("MDTM " + path)
		except ftplib.error_perm as error:
			if str(error).startswith("550"):
				return None
			if str(error)[:3] not in {"500", "501", "502", "504"}:
				raise
			self._warn_metadata()
			return None
		match = re.fullmatch(r"213 (\d{14}(?:\.\d+)?)", reply)
		if match is None:
			self._warn_metadata()
			return None
		return {"size": size, "modified": match.group(1)}

	def _warn_metadata(self) -> None:
		if not self._metadata_warning:
			print("Server modification metadata is unavailable; affected files cannot be skipped.", flush=True)
			self._metadata_warning = True

	def _enter_parent(self, parts: list[str]) -> None:
		if self._data_dir is None:
			raise RuntimeError("Enter the configured data directory before uploading")
		ftp = self._connection()
		ftp.cwd(self._data_dir)
		for part in parts:
			try:
				ftp.cwd(part)
			except ftplib.error_perm as error:
				if not str(error).startswith("550"):
					raise
				ftp.mkd(part)
				ftp.cwd(part)

	@staticmethod
	def _path_parts(relative: str) -> list[str]:
		if not isinstance(relative, str) or not relative:
			raise ValueError("Upload path must be a non-empty relative path")
		if any(char in "\\:" or ord(char) < 32 or ord(char) == 127 for char in relative):
			raise ValueError(f"Invalid upload path: {relative!r}")
		parts = relative.split("/")
		if any(part in {"", ".", ".."} for part in parts):
			raise ValueError(f"Invalid upload path: {relative!r}")
		return parts

	def _connection(self):
		if self._ftp is None:
			raise RuntimeError("FTP session is not open")
		return self._ftp

	def close(self) -> None:
		ftp, self._ftp = self._ftp, None
		self._data_dir = None
		if ftp is None:
			return
		try:
			ftp.quit()
		except ftplib.all_errors:
			pass
		finally:
			ftp.close()

	def __exit__(self, exc_type, exc_value, traceback):
		self.close()
