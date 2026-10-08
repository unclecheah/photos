"""Read non-secret preparation settings and apply command-line overrides."""

import json
import math
from dataclasses import dataclass, fields
from pathlib import Path


@dataclass(frozen=True)
class PreparationConfig:
	data_root: Path
	max_edge: int = 640
	quality: int = 85
	root_name: str = "All photos"
	ffmpeg: str | None = None
	ffprobe: str | None = None
	timeout: float = 60

	@classmethod
	def from_arguments(cls, args):
		values = cls._read(args.config) if args.config is not None else {}
		for field in fields(cls):
			value = getattr(args, field.name, None)
			if value is not None:
				values[field.name] = value
		if values.get("data_root") is None:
			raise ValueError("Provide a data directory or use --config with a data_root setting")
		# Config paths were made absolute during _read(); CLI paths use the terminal directory.
		values = cls._resolve_paths(values, Path.cwd())
		config = cls(**values)
		config._validate()
		return config

	@classmethod
	def _read(cls, file: Path) -> dict:
		file = Path(file).expanduser().resolve(strict=True)
		try:
			with file.open(encoding="utf-8-sig") as handle:
				values = json.load(handle)
		except ValueError as error:
			raise ValueError(f"Invalid JSON in {file}: {error}") from error
		if not isinstance(values, dict):
			raise ValueError("The configuration must be a JSON object")
		version = values.pop("version", None)
		if type(version) is not int or version != 1:
			raise ValueError("The configuration must have version: 1")
		unknown = values.keys() - {field.name for field in fields(cls)}
		if unknown:
			raise ValueError(f"Unknown configuration setting(s): {', '.join(sorted(unknown))}")
		return cls._resolve_paths(values, file.parent)

	@classmethod
	def _resolve_paths(cls, values: dict, base: Path) -> dict:
		values = dict(values)
		if "data_root" in values:
			value = values["data_root"]
			if not isinstance(value, (str, Path)) or not str(value).strip():
				raise ValueError("data_root must be a non-empty directory path")
			path = Path(value).expanduser()
			values["data_root"] = (path if path.is_absolute() else base / path).resolve()
		for name in ("ffmpeg", "ffprobe"):
			if name in values:
				values[name] = cls._executable(values[name], base, name)
		return values

	@staticmethod
	def _executable(value: str | None, base: Path, name: str) -> str | None:
		if value is None:
			return None
		if not isinstance(value, str) or not value.strip():
			raise ValueError(f"{name} must be null, an executable name, or a path")
		path = Path(value).expanduser()
		if path.is_absolute() or "/" in value or "\\" in value or value.startswith("~"):
			return str((path if path.is_absolute() else base / path).resolve())
		return value  # A bare name, such as ffmpeg.exe, is looked up on PATH.

	def _validate(self) -> None:
		if type(self.max_edge) is not int or not 1 <= self.max_edge <= 8192:
			raise ValueError("max_edge must be an integer between 1 and 8192")
		if type(self.quality) is not int or not 1 <= self.quality <= 95:
			raise ValueError("quality must be an integer between 1 and 95")
		if type(self.timeout) not in (int, float) or not math.isfinite(self.timeout) or self.timeout <= 0:
			raise ValueError("timeout must be a positive number")
		if not isinstance(self.root_name, str) or not self.root_name.strip():
			raise ValueError("root_name must be a non-empty string")
