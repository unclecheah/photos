<?php

declare(strict_types=1);

final class FolderService {
	private string $indexRoot;

	public function __construct(string $indexRoot) {
		$resolved = realpath($indexRoot);

		if ($resolved === false || !is_dir($resolved)) {
			throw new RuntimeException('The folder-index directory does not exist.');
		}

		$this->indexRoot = $resolved;
	}

	public function getFolder(string $path = ''): array {
		$this->validatePath($path);

		$file = $this->resolveIndex($path);
		$index = $this->readIndex($file);

		return [
			'path' => $path,
			'name' => $index['name'],
			'breadcrumbs' => $this->breadcrumbs($path),
			'folders' => $index['folders'],
			'media' => $index['media']
		];
	}

	private function validatePath(string $path): void {
		if ($path === '') return;

		if (
			str_contains($path, '\\')
			|| preg_match('/[\x00-\x1F\x7F:]/', $path)
			|| preg_match('//u', $path) !== 1
		) {
			throw new InvalidArgumentException('Invalid folder path.');
		}

		foreach (explode('/', $path) as $part) {
			if ($part === '' || $part === '.' || $part === '..') {
				throw new InvalidArgumentException('Invalid folder path.');
			}
		}
	}

	private function resolveIndex(string $path): string {
		$relative = $path === '' ? 'index.json' : $path . '/index.json';
		$file = realpath($this->indexRoot . '/' . $relative);

		if ($file === false || !is_file($file)) {
			throw new OutOfBoundsException('Folder not found.');
		}

		$prefix = $this->indexRoot . DIRECTORY_SEPARATOR;
		$length = strlen($prefix);

		$insideRoot = DIRECTORY_SEPARATOR === '\\'
			? strncasecmp($file, $prefix, $length) === 0
			: strncmp($file, $prefix, $length) === 0;

		if (!$insideRoot) {
			throw new OutOfBoundsException('Folder not found.');
		}

		return $file;
	}

	private function readIndex(string $file): array {
		$json = file_get_contents($file);

		if ($json === false) {
			throw new RuntimeException('Unable to read the folder index.');
		}

		$index = json_decode($json, true, 512, JSON_THROW_ON_ERROR);

		$valid = is_array($index)
			&& ($index['version'] ?? null) === 1
			&& is_string($index['name'] ?? null)
			&& is_array($index['folders'] ?? null)
			&& is_array($index['media'] ?? null);

		if (
			!$valid
			|| !array_is_list($index['folders'])
			|| !array_is_list($index['media'])
		) {
			throw new RuntimeException('Invalid folder-index format.');
		}

		return $index;
	}

	private function breadcrumbs(string $path): array {
		$result = [['name' => 'Home', 'path' => '']];
		$current = '';

		if ($path === '') return $result;

		foreach (explode('/', $path) as $part) {
			$current = $current === '' ? $part : $current . '/' . $part;
			$result[] = ['name' => $part, 'path' => $current];
		}

		return $result;
	}
}
