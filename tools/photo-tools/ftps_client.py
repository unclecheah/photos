"""Verified explicit-FTPS session. This step exposes read-only operations."""

import ftplib
import ssl

from upload_config import UploadConfig


class FtpsClient:

	def __init__(self, config: UploadConfig):
		self.config = config
		self._ftp = None

	def __enter__(self):
		context = ssl.create_default_context()
		ftp = ftplib.FTP_TLS(context=context, timeout=self.config.timeout, encoding="utf-8")
		try:
			ftp.connect(self.config.host, self.config.port)
			ftp.auth()  # Verify TLS before credentials are requested or transmitted.
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
		ftp.prot_p()  # Encrypt directory listings and later file-transfer connections.
		ftp.set_pasv(True)

	def working_directory(self) -> str:
		return self._connection().pwd()

	def enter_data_directory(self) -> str:
		ftp = self._connection()
		ftp.cwd(self.config.remote_data_dir)
		return ftp.pwd()

	def list_names(self) -> list[str]:
		return self._connection().nlst()

	def _connection(self):
		if self._ftp is None:
			raise RuntimeError("FTPS session is not open")
		return self._ftp

	def close(self) -> None:
		ftp, self._ftp = self._ftp, None
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
