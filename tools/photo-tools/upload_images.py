"""Stage smaller upload photos and matching indexes without editing local originals."""

import json
import warnings
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps

from upload_planner import UploadItem, UploadPlan


@dataclass(frozen=True)
class PreparedUploadItem(UploadItem):
	source_item: UploadItem

	def check_unchanged(self) -> None:
		super().check_unchanged()
		self.source_item.check_unchanged()


class UploadImagePreparer:

	def __init__(self, staging_root: Path, max_edge: int = 1920, quality: int = 90):
		if type(max_edge) is not int or not 1 <= max_edge <= 8192:
			raise ValueError("photo_max_edge must be an integer between 1 and 8192")
		if type(quality) is not int or not 1 <= quality <= 95:
			raise ValueError("photo_quality must be an integer between 1 and 95")
		self.root = Path(staging_root)
		self.max_edge = max_edge
		self.quality = quality

	def prepare(self, plan: UploadPlan) -> UploadPlan:
		items = {item.relative_path: item for item in plan.items}
		indexes = self._read_indexes(plan)
		resized = 0
		for index_item, document in indexes:
			changed = False
			for entry in document["media"]:
				if entry["type"] != "photo":
					continue
				path = "max/" + entry["id"]
				original = items[path]
				prepared, size = self._photo(original)
				items[path] = prepared
				resized += prepared is not original
				if (entry["width"], entry["height"]) != size:
					entry["width"], entry["height"] = size
					changed = True
			if changed:
				items[index_item.relative_path] = self._index(index_item, document)
		for item in items.values():
			item.check_unchanged()
		print(f"Prepared {resized} resized upload photos; longest edge limited to {self.max_edge}px.", flush=True)
		return UploadPlan(tuple(items[item.relative_path] for item in plan.items))

	@staticmethod
	def _read_indexes(plan: UploadPlan) -> list:
		indexes = []
		for item in plan.items:
			if item.kind != "index":
				continue
			item.check_unchanged()
			with item.local_file.open(encoding="utf-8") as handle:
				document = json.load(handle)
			item.check_unchanged()
			indexes.append((item, document))
		return indexes

	def _photo(self, item: UploadItem) -> tuple[UploadItem, tuple[int, int]]:
		item.check_unchanged()
		with warnings.catch_warnings():
			warnings.simplefilter("error", Image.DecompressionBombWarning)
			with Image.open(item.local_file, formats=["JPEG", "PNG", "WEBP"]) as original:
				if getattr(original, "n_frames", 1) != 1:
					raise ValueError(f"Animated photo is not supported: {item.relative_path}")
				with ImageOps.exif_transpose(original) as oriented:
					if max(oriented.size) <= self.max_edge:
						item.check_unchanged()
						return item, oriented.size
					output = self._destination(item)
					print(f"Resizing for upload: {item.relative_path}", flush=True)
					with self._working_image(oriented) as image:
						image.thumbnail((self.max_edge, self.max_edge), Image.Resampling.LANCZOS)
						self._save(image, original.format, oriented.info.get("icc_profile"), output)
						size = image.size
		item.check_unchanged()
		return self._prepared(item, output), size

	@staticmethod
	def _working_image(image: Image.Image) -> Image.Image:
		# Expand palettes/transparency before resampling to preserve alpha and use Lanczos.
		if image.mode in {"P", "1"} or "transparency" in image.info:
			return image.convert("RGBA")
		return image.copy()

	def _save(self, image: Image.Image, format_name: str, profile: bytes | None, output: Path) -> None:
		options = {"icc_profile": profile} if profile else {}
		if format_name == "JPEG":
			options.update(quality=self.quality, optimize=True)
		elif format_name == "WEBP":
			options.update(quality=self.quality, method=6)
		# Orientation is applied to pixels. Omit the old EXIF dimensions/orientation.
		image.info.clear()
		image.save(output, format=format_name, **options)

	def _index(self, item: UploadItem, document: dict) -> PreparedUploadItem:
		output = self._destination(item)
		with output.open("w", encoding="utf-8", newline="\n") as handle:
			json.dump(document, handle, ensure_ascii=False, indent="\t", allow_nan=False)
			handle.write("\n")
		return self._prepared(item, output)

	def _destination(self, item: UploadItem) -> Path:
		output = self.root.joinpath(*item.relative_path.split("/"))
		if not output.resolve().is_relative_to(self.root.resolve()):
			raise ValueError("Upload staging path escapes its directory")
		output.parent.mkdir(parents=True, exist_ok=True)
		return output

	@staticmethod
	def _prepared(source: UploadItem, file: Path) -> PreparedUploadItem:
		stat = file.stat()
		return PreparedUploadItem(file, source.relative_path, source.kind,
			stat.st_size, stat.st_mtime_ns, source)
