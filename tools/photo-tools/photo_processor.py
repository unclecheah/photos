"""Read photo metadata and create JPEG thumbnails locally. Python 3.12+."""

import io
import tempfile
import warnings
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageCms, ImageOps

from media_scanner import SourceMedia


@dataclass(frozen=True)
class PhotoResult:
	path: str
	width: int
	height: int
	thumbnail_file: Path
	thumbnail_path: str
	thumbnail_width: int
	thumbnail_height: int


class PhotoProcessor:
	"""Keep originals untouched; write generated files beneath thumbnail_root."""

	def __init__(self, max_root: Path, thumbnail_root: Path, *, max_edge=640, quality=85):
		self.max_root = Path(max_root).resolve(strict=True)
		self.thumbnail_root = Path(thumbnail_root).resolve()
		self._validate_roots()
		if not isinstance(max_edge, int) or not 1 <= max_edge <= 8192:
			raise ValueError("max_edge must be an integer between 1 and 8192")
		if not isinstance(quality, int) or not 1 <= quality <= 95:
			raise ValueError("quality must be an integer between 1 and 95")
		self.max_edge = max_edge
		self.quality = quality
		self.srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB"))

	def _validate_roots(self) -> None:
		if not self.max_root.is_dir():
			raise NotADirectoryError(self.max_root)
		if self.thumbnail_root.is_relative_to(self.max_root):
			raise ValueError("Thumbnail output must be outside data/max")
		if self.max_root.is_relative_to(self.thumbnail_root):
			raise ValueError("Thumbnail output must not contain data/max")
		if self.thumbnail_root.exists() and not self.thumbnail_root.is_dir():
			raise NotADirectoryError(self.thumbnail_root)

	def prepare(self, source: SourceMedia) -> PhotoResult:
		if source.type != "photo":
			raise ValueError("PhotoProcessor expects a photo")
		file = source.file.resolve(strict=True)
		relative = file.relative_to(self.max_root)
		if relative.as_posix() != source.path:
			raise ValueError("Source path does not match its gallery path")
		output = self._output_file(relative)
		with warnings.catch_warnings():
			warnings.simplefilter("error", Image.DecompressionBombWarning)
			width, height, thumb_width, thumb_height = self._prepare_image(file, output)
		return PhotoResult(source.path, width, height, output,
			output.relative_to(self.thumbnail_root).as_posix(), thumb_width, thumb_height)

	def _output_file(self, relative: Path) -> Path:
		output = self.thumbnail_root / relative.parent / (relative.name + ".jpg")
		# Reject redirected paths before creating directories or replacing files.
		if not output.resolve().is_relative_to(self.thumbnail_root):
			raise ValueError("Thumbnail path escapes its output directory")
		if output.is_symlink():
			raise ValueError("Thumbnail destination is a symbolic link")
		return output

	def _prepare_image(self, file: Path, output: Path) -> tuple[int, int, int, int]:
		with Image.open(file, formats=["JPEG", "PNG", "WEBP"]) as original:
			if getattr(original, "n_frames", 1) != 1:
				raise ValueError("Animated images are not supported in this photo step")
			with ImageOps.exif_transpose(original) as oriented:
				width, height = oriented.size
				oriented.thumbnail((self.max_edge, self.max_edge), Image.Resampling.LANCZOS)
				with self._jpeg_image(oriented) as thumbnail:
					self._save_atomic(thumbnail, output)
					return width, height, thumbnail.width, thumbnail.height

	def _jpeg_image(self, image: Image.Image) -> Image.Image:
		# A neutral white matte makes transparent PNG/WebP files valid JPEGs.
		with image.convert("RGBA") as rgba:
			with rgba.getchannel("A") as alpha:
				with self._srgb_image(image) as rgb:
					output = Image.new("RGB", image.size, "white")
					output.paste(rgb, mask=alpha)
		return output

	def _srgb_image(self, image: Image.Image) -> Image.Image:
		profile = image.info.get("icc_profile")
		if not profile:
			return image.convert("RGB")
		try:
			input_profile = ImageCms.ImageCmsProfile(io.BytesIO(profile))
			mode = image.mode if image.mode in {"RGB", "CMYK", "L"} else "RGB"
			with image.convert(mode) as compatible:
				return ImageCms.profileToProfile(compatible, input_profile, self.srgb, outputMode="RGB")
		except (OSError, ImageCms.PyCMSError) as error:
			raise ValueError(f"Cannot convert embedded colour profile: {error}") from error

	def _save_atomic(self, image: Image.Image, output: Path) -> None:
		output.parent.mkdir(parents=True, exist_ok=True)
		temporary = None
		try:
			with tempfile.NamedTemporaryFile(dir=output.parent, prefix=".thumb-", suffix=".tmp", delete=False) as handle:
				temporary = Path(handle.name)
				image.save(handle, format="JPEG", quality=self.quality, optimize=True,
					icc_profile=self.srgb.tobytes())
			# The temporary file is closed first, which is required on Windows.
			temporary.replace(output)
		finally:
			if temporary is not None:
				temporary.unlink(missing_ok=True)
