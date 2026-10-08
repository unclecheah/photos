"""Inspect local videos and generate JPEG stills. Originals are unchanged."""

import io
import json
import math
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from PIL import Image

from media_scanner import SourceMedia


class VideoProcessingError(Exception):
	pass


@dataclass(frozen=True)
class VideoInfo:
	stream_index: int
	width: int
	height: int
	duration_seconds: float | None
	codec: str
	rotation: int


@dataclass(frozen=True)
class VideoResult:
	path: str
	width: int
	height: int
	duration_seconds: float | None
	duration: str | None
	codec: str
	thumbnail_file: Path
	thumbnail_path: str
	thumbnail_width: int
	thumbnail_height: int
	poster_seconds: float


class VideoProcessor:

	def __init__(self, max_root: Path, thumbnail_root: Path, *, max_edge=640,
		quality=85, ffmpeg=None, ffprobe=None, timeout=60):
		self.max_root = Path(max_root).resolve(strict=True)
		self.thumbnail_root = Path(thumbnail_root).resolve()
		self._validate_roots()
		if not isinstance(max_edge, int) or not 1 <= max_edge <= 8192:
			raise ValueError("max_edge must be an integer between 1 and 8192")
		if not isinstance(quality, int) or not 1 <= quality <= 95:
			raise ValueError("quality must be an integer between 1 and 95")
		if not math.isfinite(timeout) or timeout <= 0:
			raise ValueError("timeout must be a positive number")
		self.max_edge, self.quality, self.timeout = max_edge, quality, timeout
		self.ffmpeg = self._find_tool("ffmpeg", ffmpeg)
		self.ffprobe = self._find_tool("ffprobe", ffprobe)

	def _validate_roots(self) -> None:
		if not self.max_root.is_dir():
			raise NotADirectoryError(self.max_root)
		if self.thumbnail_root.is_relative_to(self.max_root):
			raise ValueError("Thumbnail output must be outside data/max")
		if self.max_root.is_relative_to(self.thumbnail_root):
			raise ValueError("Thumbnail output must not contain data/max")
		if self.thumbnail_root.exists() and not self.thumbnail_root.is_dir():
			raise NotADirectoryError(self.thumbnail_root)

	@staticmethod
	def _find_tool(name: str, supplied: str | None) -> str:
		if supplied:
			found = shutil.which(supplied)
		else:
			executable = name + (".exe" if os.name == "nt" else "")
			local = Path(__file__).resolve().parents[1] / "ffmpeg" / "bin" / executable
			found = shutil.which(str(local)) or shutil.which(name)
		if not found:
			raise VideoProcessingError(
				f"Cannot find {name}. Put it in tools/ffmpeg/bin, add it to PATH, "
				f"or provide --{name} with its executable path.")
		return str(Path(found).resolve())

	def prepare(self, source: SourceMedia) -> VideoResult:
		if source.type != "video":
			raise ValueError("VideoProcessor expects a video")
		file = source.file.resolve(strict=True)
		relative = file.relative_to(self.max_root)
		if relative.as_posix() != source.path:
			raise ValueError("Source path does not match its gallery path")
		output = self._output_file(relative)
		info = self._probe(file)
		png, seconds = self._extract_frame(file, info)
		thumb_width, thumb_height = self._save_thumbnail(png, output)
		return VideoResult(source.path, info.width, info.height, info.duration_seconds,
			self._format_duration(info.duration_seconds), info.codec, output,
			output.relative_to(self.thumbnail_root).as_posix(), thumb_width, thumb_height, seconds)

	def _output_file(self, relative: Path) -> Path:
		output = self.thumbnail_root / relative.parent / (relative.name + ".jpg")
		if not output.resolve().is_relative_to(self.thumbnail_root):
			raise ValueError("Thumbnail path escapes its output directory")
		if output.is_symlink():
			raise ValueError("Thumbnail destination is a symbolic link")
		return output

	def _run(self, arguments: list[str]) -> bytes:
		try:
			result = subprocess.run(arguments, stdin=subprocess.DEVNULL,
				capture_output=True, timeout=self.timeout, check=False)
		except subprocess.TimeoutExpired as error:
			raise VideoProcessingError(f"{Path(arguments[0]).name} timed out after {self.timeout}s") from error
		except OSError as error:
			raise VideoProcessingError(str(error)) from error
		if result.returncode:
			message = result.stderr.decode("utf-8", errors="replace").strip()
			raise VideoProcessingError(message[-2000:] or "Video command failed")
		return result.stdout

	def _probe(self, file: Path) -> VideoInfo:
		data = json.loads(self._run([
			self.ffprobe, "-v", "error", "-select_streams", "V:0",
			"-show_streams", "-show_format", "-of", "json", str(file)
		]))
		streams = data.get("streams", [])
		if not streams:
			raise VideoProcessingError("No video stream was found (cover art does not count)")
		stream = streams[0]
		if stream.get("color_transfer") in {"smpte2084", "arib-std-b67"}:
			raise VideoProcessingError("HDR video needs tone mapping, which is not implemented in this step")
		rotation = self._rotation(stream)
		width, height = self._display_size(stream, rotation)
		duration = self._positive_number(stream.get("duration"))
		if duration is None:
			duration = self._positive_number(data.get("format", {}).get("duration"))
		return VideoInfo(int(stream["index"]), width, height, duration,
			str(stream.get("codec_name", "unknown")), rotation)

	@staticmethod
	def _rotation(stream: dict) -> int:
		value = stream.get("tags", {}).get("rotate", 0)
		for side_data in stream.get("side_data_list", []):
			if "rotation" in side_data:
				value = side_data["rotation"]
				break
		angle = float(value)
		if not math.isfinite(angle):
			raise VideoProcessingError("Invalid video rotation metadata")
		quarter_turns = round(angle / 90)
		if abs(angle - quarter_turns * 90) > 0.1:
			raise VideoProcessingError("This step supports only 0, 90, 180 and 270 degree video rotation")
		return (quarter_turns * 90) % 360

	@staticmethod
	def _display_size(stream: dict, rotation: int) -> tuple[int, int]:
		width, height = int(stream.get("width", 0)), int(stream.get("height", 0))
		if width <= 0 or height <= 0:
			raise VideoProcessingError("Video dimensions are missing or invalid")
		ratio = stream.get("sample_aspect_ratio")
		if ratio not in {None, "N/A", "0:1", "0:0"}:
			try:
				sar = Fraction(str(ratio).replace(":", "/"))
			except (ValueError, ZeroDivisionError) as error:
				raise VideoProcessingError("Invalid sample aspect ratio") from error
			if sar <= 0:
				raise VideoProcessingError("Invalid sample aspect ratio")
			width = max(1, round(width * sar))
		return (height, width) if rotation in {90, 270} else (width, height)

	@staticmethod
	def _positive_number(value) -> float | None:
		try:
			number = float(value)
		except (TypeError, ValueError):
			return None
		return number if math.isfinite(number) and number > 0 else None

	@staticmethod
	def _format_duration(seconds: float | None) -> str | None:
		if seconds is None:
			return None
		minutes, seconds = divmod(int(seconds), 60)
		hours, minutes = divmod(minutes, 60)
		return f"{hours}:{minutes:02}:{seconds:02}" if hours else f"{minutes}:{seconds:02}"

	def _extract_frame(self, file: Path, info: VideoInfo) -> tuple[bytes, float]:
		seconds = min(1.0, info.duration_seconds / 2) if info.duration_seconds else 0.0
		try:
			return self._frame_at(file, info, seconds), seconds
		except VideoProcessingError:
			if seconds == 0:
				raise
		# Some short or poorly indexed files cannot seek reliably.
		return self._frame_at(file, info, 0.0), 0.0

	def _frame_at(self, file: Path, info: VideoInfo, seconds: float) -> bytes:
		ratio = min(1.0, self.max_edge / max(info.width, info.height))
		width, height = max(1, round(info.width * ratio)), max(1, round(info.height * ratio))
		arguments = [self.ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin"]
		if seconds > 0:
			arguments.extend(["-ss", f"{seconds:.6f}"])
		arguments.extend([
			"-i", str(file), "-map", f"0:{info.stream_index}", "-frames:v", "1",
			"-vf", f"scale={width}:{height}:flags=lanczos,setsar=1",
			"-an", "-sn", "-dn", "-c:v", "png", "-pix_fmt", "rgb24",
			"-f", "image2pipe", "pipe:1"
		])
		# FFmpeg autorotation is enabled by default, before the scale filter.
		png = self._run(arguments)
		if not png:
			raise VideoProcessingError("No video frame was decoded")
		return png

	def _save_thumbnail(self, png: bytes, output: Path) -> tuple[int, int]:
		with Image.open(io.BytesIO(png), formats=["PNG"]) as frame:
			with frame.convert("RGB") as image:
				self._save_atomic(image, output)
				return image.size

	def _save_atomic(self, image: Image.Image, output: Path) -> None:
		output.parent.mkdir(parents=True, exist_ok=True)
		temporary = None
		try:
			with tempfile.NamedTemporaryFile(dir=output.parent, prefix=".video-", suffix=".tmp", delete=False) as handle:
				temporary = Path(handle.name)
				image.save(handle, format="JPEG", quality=self.quality, optimize=True)
			temporary.replace(output)
		finally:
			if temporary is not None:
				temporary.unlink(missing_ok=True)
