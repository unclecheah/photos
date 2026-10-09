<?php
declare(strict_types=1);

/** Local PHP development server only; full-size videos support byte ranges. */
final class DevVideoResponse
{
	private const TYPES = [
		'mp4' => 'video/mp4',
		'm4v' => 'video/mp4',
		'webm' => 'video/webm',
		'ogv' => 'video/ogg',
		'mov' => 'video/quicktime',
	];

	public static function handles(string $path): bool
	{
		$extension = strtolower(pathinfo($path, PATHINFO_EXTENSION));
		return str_starts_with($path, '/data/max/') && isset(self::TYPES[$extension]);
	}

	public function send(string $path, string $root): void
	{
		$method = $_SERVER['REQUEST_METHOD'] ?? 'GET';
		if (!in_array($method, ['GET', 'HEAD'], true)) {
			header('Allow: GET, HEAD');
			$this->emptyResponse(405);
			return;
		}

		$file = $this->resolveFile($path, $root);
		$stream = $file === null ? false : @fopen($file, 'rb');
		if ($stream === false) {
			$this->emptyResponse(404);
			return;
		}

		try {
			$stat = fstat($stream);
			if ($stat === false) {
				$this->emptyResponse(500);
				return;
			}
			$this->sendStream($stream, $path, $stat, $method);
		} finally {
			fclose($stream);
		}
	}

	private function resolveFile(string $path, string $root): ?string
	{
		if (str_contains($path, "\0") || str_contains($path, '\\')) return null;
		$relative = substr($path, strlen('/data/max/'));
		foreach (explode('/', $relative) as $part) {
			if ($part === '..' || $part === '.') return null;
		}

		$base = realpath($root);
		if ($base === false) return null;
		$file = realpath($base . DIRECTORY_SEPARATOR . $relative);
		if ($file === false || !is_file($file)) return null;

		// Resolve symlinks before checking containment; Windows paths ignore case.
		$prefix = rtrim($base, DIRECTORY_SEPARATOR) . DIRECTORY_SEPARATOR;
		$inside = PHP_OS_FAMILY === 'Windows'
			? strncasecmp($file, $prefix, strlen($prefix)) === 0
			: str_starts_with($file, $prefix);
		return $inside ? $file : null;
	}

	private function sendStream($stream, string $path, array $stat, string $method): void
	{
		$size = (int) $stat['size'];
		$modified = gmdate('D, d M Y H:i:s', (int) $stat['mtime']) . ' GMT';
		$range = $method === 'GET' ? ($_SERVER['HTTP_RANGE'] ?? '') : '';
		if (isset($_SERVER['HTTP_IF_RANGE']) && $_SERVER['HTTP_IF_RANGE'] !== $modified) {
			$range = ''; // A stale or unsupported validator requires the whole file.
		}

		@ini_set('zlib.output_compression', '0');
		while (ob_get_level() > 0) ob_end_clean();
		header('Content-Type: ' . self::TYPES[strtolower(pathinfo($path, PATHINFO_EXTENSION))]);
		header('Accept-Ranges: bytes');
		header('Last-Modified: ' . $modified);
		header('Cache-Control: no-store');
		header('X-Content-Type-Options: nosniff');

		$bytes = $this->parseRange($range, $size);
		if ($bytes === false) {
			header('Content-Range: bytes */' . $size);
			$this->emptyResponse(416);
			return;
		}
		[$start, $end, $partial] = $bytes;
		$length = max(0, $end - $start + 1);
		if ($length > 0 && fseek($stream, $start) !== 0) {
			$this->emptyResponse(500);
			return;
		}

		http_response_code($partial ? 206 : 200);
		if ($partial) header("Content-Range: bytes $start-$end/$size");
		header('Content-Length: ' . $length);
		if ($method !== 'HEAD') $this->copyBytes($stream, $length);
	}

	/** Invalid syntax and multipart ranges are ignored; unsatisfiable ranges are 416. */
	private function parseRange(string $range, int $size): array|false
	{
		if (!preg_match('/^bytes=(\d*)-(\d*)$/D', trim($range), $match)
			|| ($match[1] === '' && $match[2] === '')) {
			return [0, $size - 1, false];
		}
		if ($size === 0) return false;
		if ($match[1] === '') {
			$count = (int) $match[2];
			return $count > 0 ? [max(0, $size - $count), $size - 1, true] : false;
		}

		$start = (int) $match[1];
		$end = $match[2] === '' ? $size - 1 : min((int) $match[2], $size - 1);
		return $start < $size && $end >= $start ? [$start, $end, true] : false;
	}

	private function copyBytes($stream, int $remaining): void
	{
		while ($remaining > 0 && !feof($stream) && !connection_aborted()) {
			$chunk = fread($stream, min(65536, $remaining));
			if ($chunk === false || $chunk === '') break;
			echo $chunk;
			$remaining -= strlen($chunk);
			flush();
		}
	}

	private function emptyResponse(int $status): void
	{
		http_response_code($status);
		header('Content-Length: 0');
	}
}

if (PHP_SAPI !== 'cli-server') {
	http_response_code(404);
	return;
}

$path = rawurldecode(explode('?', $_SERVER['REQUEST_URI'] ?? '/', 2)[0]);
if (!DevVideoResponse::handles($path)) return false;

(new DevVideoResponse())->send($path, __DIR__ . '/public/data/max');
return true;
