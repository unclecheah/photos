"""Incremental gallery uploads: media first, deepest indexes first, root last."""

import hashlib
from time import monotonic

from ftp_client import FtpClient
from upload_cache import UploadCache
from upload_planner import UploadItem, UploadPlan


class GalleryUploader:

	def __init__(self, client: FtpClient, cache: UploadCache | None = None, force: bool = False):
		self.client = client
		self.cache = cache
		self.force = force
		self.completed = 0
		self.skipped = 0

	def upload(self, plan: UploadPlan) -> int:
		self.completed = 0
		self.skipped = 0
		media = [item for item in plan.items if item.kind != "index"]
		indexes = sorted(
			(item for item in plan.items if item.kind == "index"),
			key=lambda item: (-item.relative_path.count("/"), item.relative_path)
		)
		self._check_all(plan)
		try:
			self._upload_group(media, len(plan.items))
			# Do not publish indexes if the local inventory changed during media upload.
			self._check_all(plan)
			print("All media uploaded or verified unchanged. Checking indexes...", flush=True)
			self._upload_group(indexes, len(plan.items))
		except BaseException:
			print(f"Stopped after {self.completed} uploads and {self.skipped} skips. Saved receipts remain available for retry.", flush=True)
			raise
		return self.completed

	@staticmethod
	def _check_all(plan: UploadPlan) -> None:
		for item in plan.items:
			item.check_unchanged()

	def _upload_group(self, items: list[UploadItem], total: int) -> None:
		for item in items:
			print(f"[{self.completed + self.skipped + 1}/{total}] {item.kind}: {item.relative_path} ({item.size:,} bytes)", flush=True)
			digest = UploadCache.fingerprint(item)
			if self._can_skip(item, digest):
				self.skipped += 1
				print("  Skipped: unchanged locally and remote metadata matches.", flush=True)
				continue
			if self.cache is not None:
				self.cache.forget(item.relative_path)
			self._upload_one(item, digest)
			self.completed += 1
			print("  Published.", flush=True)
			self._remember(item, digest)

	def _can_skip(self, item: UploadItem, digest: str) -> bool:
		if self.force or self.cache is None or not self.cache.has_digest(item.relative_path, digest):
			return False
		remote = self.client.file_signature(item.relative_path)
		item.check_unchanged()
		return (remote is not None and remote["size"] == item.size
			and self.cache.matches(item.relative_path, digest, remote))

	def _remember(self, item: UploadItem, digest: str) -> None:
		if self.cache is None:
			return
		remote = self.client.file_signature(item.relative_path)
		if remote is not None and remote["size"] != item.size:
			raise ValueError(f"Published file size changed: {item.relative_path}")
		self.cache.remember(item.relative_path, digest, remote)

	def _upload_one(self, item: UploadItem, digest: str) -> None:
		item.check_unchanged()
		progress = TransferProgress(item.size)
		temporary, destination = self.client.stage_file(
			item.local_file, item.relative_path, progress.advance
		)
		try:
			item.check_unchanged()
			if progress.digest.hexdigest() != digest:
				raise ValueError(f"Local file content changed during upload: {item.relative_path}")
			if progress.sent != item.size or self.client.remote_size(temporary) != item.size:
				raise ValueError(f"Uploaded byte count does not match: {item.relative_path}")
			self.client.publish_file(temporary, destination)
		except BaseException:
			print(f"Publication did not complete; check temporary/destination files: {temporary} -> {destination}", flush=True)
			raise


class TransferProgress:

	def __init__(self, total: int):
		self.total = total
		self.sent = 0
		self.digest = hashlib.sha256()
		self.last_report = monotonic()

	def advance(self, block: bytes) -> None:
		self.sent += len(block)
		self.digest.update(block)
		now = monotonic()
		if now - self.last_report >= 2:
			print(f"  Sent {self.sent:,} / {self.total:,} bytes", flush=True)
			self.last_report = now
