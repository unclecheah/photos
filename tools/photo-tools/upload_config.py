"""Read non-secret connection settings for plain FTP."""

import json
import math
from dataclasses import dataclass, fields
from pathlib import Path


@dataclass(frozen=True)
class UploadConfig:
	host: str
	remote_data_dir: str
	protocol: str = "ftp"
	port: int = 21
	username: str = ""
	timeout: float = 30

	@classmethod
	def load(cls, path: Path):
		with Path(path).expanduser().open(encoding="utf-8-sig") as handle:
			data = json.load(handle)
		if not isinstance(data, dict):
			raise ValueError("Upload configuration must be a JSON object")
		version = data.pop("version", None)
		if type(version) is not int or version != 1:
			raise ValueError("Upload configuration must have version: 1")
		unknown = data.keys() - {field.name for field in fields(cls)}
		if unknown:
			raise ValueError(f"Unknown upload setting(s): {', '.join(sorted(unknown))}")
		if not {"host", "remote_data_dir"}.issubset(data):
			raise ValueError("Upload configuration requires host and remote_data_dir")
		config = cls(**data)
		config._validate()
		return config

	def _validate(self) -> None:
		if self.protocol != "ftp":
			raise ValueError("This connection module supports plain FTP only")
		if not isinstance(self.host, str) or not self.host:
			raise ValueError("host must be a hostname without a URL prefix")
		if any(char.isspace() or char in "/\\@?#:" or ord(char) < 32 for char in self.host):
			raise ValueError("host must contain only the hostname; put the port in port")
		if type(self.port) is not int or not 1 <= self.port <= 65535:
			raise ValueError("port must be an integer between 1 and 65535")
		if type(self.timeout) not in (int, float) or not math.isfinite(self.timeout) or self.timeout <= 0:
			raise ValueError("timeout must be a positive number")
		if not isinstance(self.username, str) or any(ord(char) < 32 for char in self.username):
			raise ValueError("username must be a string without control characters")
		self._validate_remote_directory()

	def _validate_remote_directory(self) -> None:
		path = self.remote_data_dir
		if not isinstance(path, str) or not path:
			raise ValueError("remote_data_dir must be a non-empty directory path")
		if any(char in "\\:" or ord(char) < 32 or ord(char) == 127 for char in path):
			raise ValueError("remote_data_dir must be a directory path without a URL prefix")
		if path != "/" and any(part in {"", ".", ".."} for part in path.removeprefix("/").split("/")):
			raise ValueError("remote_data_dir must not contain empty, dot or parent segments; omit trailing /")
