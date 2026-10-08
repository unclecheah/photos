"""Local, destination-specific receipts for successfully published uploads."""

import hashlib
import json
import os
import tempfile
from pathlib import Path

from upload_planner import UploadItem


class UploadCache:

	def __init__(self, target: dict, cache_dir: Path | None = None):
		self.target = target
		key = hashlib.sha256(json.dumps(target, sort_keys=True).encode("utf-8")).hexdigest()
		base = cache_dir if cache_dir is not None else Path(__file__).resolve().parent / ".cache"
		self.file = base / f"uploads-{key}.json"
		self.entries = self._read()

	def _read(self) -> dict:
		try:
			data = json.loads(self.file.read_text(encoding="utf-8"))
		except FileNotFoundError:
			return {}
		except (ValueError, UnicodeError):
			print("Upload cache is unreadable; files will be uploaded again.")
			return {}
		if not isinstance(data, dict) or data.get("version") != 1 or data.get("target") != self.target:
			return {}
		entries = data.get("entries")
		return entries if isinstance(entries, dict) else {}

	@staticmethod
	def fingerprint(item: UploadItem) -> str:
		item.check_unchanged()
		digest = hashlib.sha256()
		with item.local_file.open("rb") as handle:
			while block := handle.read(1024 * 1024):
				digest.update(block)
		item.check_unchanged()
		return digest.hexdigest()

	def matches(self, path: str, digest: str, remote: dict | None) -> bool:
		entry = self.entries.get(path)
		return (
			remote is not None and isinstance(entry, dict)
			and entry.get("sha256") == digest and entry.get("remote") == remote
		)

	def has_digest(self, path: str, digest: str) -> bool:
		entry = self.entries.get(path)
		return isinstance(entry, dict) and entry.get("sha256") == digest

	def forget(self, path: str) -> None:
		if path in self.entries:
			del self.entries[path]
			self.save()

	def remember(self, path: str, digest: str, remote: dict | None) -> None:
		if remote is not None:
			self.entries[path] = {"sha256": digest, "remote": remote}
			self.save()

	def save(self) -> None:
		self.file.parent.mkdir(parents=True, exist_ok=True)
		temporary = None
		try:
			with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.file.parent,
				prefix=".upload-cache-", suffix=".tmp", delete=False) as handle:
				temporary = Path(handle.name)
				json.dump({"version": 1, "target": self.target, "entries": self.entries},
					handle, ensure_ascii=False, indent="\t", allow_nan=False)
				handle.flush()
				os.fsync(handle.fileno())
			temporary.replace(self.file)
		finally:
			if temporary is not None:
				temporary.unlink(missing_ok=True)
