"""Run: py -m unittest discover -s tools/photo-tools -p "test_*.py" -v"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from media_scanner import MediaScanner


class MediaScannerTests(unittest.TestCase):

	def setUp(self):
		self.temp = tempfile.TemporaryDirectory()
		self.addCleanup(self.temp.cleanup)
		self.root = Path(self.temp.name) / "max"
		self.root.mkdir()

	def add_file(self, path: str) -> Path:
		file = self.root / path
		file.parent.mkdir(parents=True, exist_ok=True)
		file.write_bytes(b"scanner fixture; not actual media")
		return file

	def test_natural_order_and_direct_folder_contents(self):
		for path in ["10.jpg", "2.JPG", "Japan/flower.MP4", "Japan/Kyoto/1.png"]:
			self.add_file(path)
		(self.root / "Empty").mkdir()
		result = MediaScanner(self.root).scan()
		folders = {folder.path: folder for folder in result.folders}
		self.assertEqual(list(folders), ["", "Empty", "Japan", "Japan/Kyoto"])
		self.assertEqual(folders[""].folders, ["Empty", "Japan"])
		self.assertEqual([item.path for item in folders[""].media], ["2.JPG", "10.jpg"])
		self.assertEqual(folders["Japan"].media[0].type, "video")
		self.assertEqual(folders["Japan"].folders, ["Japan/Kyoto"])
		self.assertEqual(folders["Empty"].media, [])

	def test_names_and_distinct_same_stem_files_are_preserved(self):
		for path in ["日本 trip/flower.jpg", "日本 trip/flower.mp4", "日本 trip/a #%.png"]:
			self.add_file(path)
		folder = MediaScanner(self.root).scan().folders[1]
		self.assertEqual(folder.path, "日本 trip")
		self.assertEqual([item.path for item in folder.media], [
			"日本 trip/a #%.png", "日本 trip/flower.jpg", "日本 trip/flower.mp4"
		])
		self.assertTrue(all(item.file.is_absolute() for item in folder.media))

	def test_skips_are_visible_and_scan_does_not_modify_files(self):
		for path in ["notes.txt", "phone.heic", ".private/1.jpg", "photo.jpg"]:
			self.add_file(path)
		before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
		result = MediaScanner(self.root).scan()
		self.assertEqual({path for path, _ in result.skipped}, {"notes.txt", "phone.heic", ".private"})
		self.assertEqual(len(result.folders), 1)
		after = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
		self.assertEqual(before, after)

	def test_missing_root_and_file_root_fail(self):
		with self.assertRaises(FileNotFoundError):
			MediaScanner(self.root / "missing")
		file = self.add_file("1.jpg")
		with self.assertRaises(NotADirectoryError):
			MediaScanner(file)

	def test_directory_link_is_not_followed(self):
		link = self.root / "loop"
		try:
			link.symlink_to(self.root, target_is_directory=True)
		except (OSError, NotImplementedError):
			self.skipTest("Creating symbolic links is not permitted here")
		result = MediaScanner(self.root).scan()
		self.assertEqual(len(result.folders), 1)
		self.assertEqual(result.skipped, [("loop", "symbolic link or junction")])

	def test_command_line_runs_from_another_directory(self):
		self.add_file("2.jpg")
		script = Path(__file__).with_name("media_scanner.py")
		command = [sys.executable, str(script), str(self.root)]
		result = subprocess.run(command, cwd=self.temp.name, capture_output=True, text=True)
		self.assertEqual(result.returncode, 0, result.stderr)
		self.assertIn("1 photos, 0 videos", result.stdout)
		command[-1] = str(self.root / "missing")
		failure = subprocess.run(command, cwd=self.temp.name, capture_output=True, text=True)
		self.assertEqual(failure.returncode, 1)
		self.assertIn("Scan failed:", failure.stderr)


if __name__ == "__main__":
	unittest.main()
