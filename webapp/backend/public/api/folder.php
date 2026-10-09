<?php

declare(strict_types=1);

ini_set('display_errors', '0');
ini_set('log_errors', '1');

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

try {
	if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
		header('Allow: GET');
		http_response_code(405);
		$result = ['error' => 'Method not allowed.'];
	} else {
		$path = $_GET['path'] ?? '';

		if (!is_string($path)) {
			throw new InvalidArgumentException('Invalid folder path.');
		}

		$backendRoot = dirname(__DIR__, 2);
		require_once $backendRoot . '/privatePhoto/FolderService.php';

		$service = new FolderService(dirname(__DIR__) . '/data/index');
		$result = $service->getFolder($path);
	}
} catch (InvalidArgumentException $error) {
	http_response_code(400);
	$result = ['error' => 'Invalid folder path.'];
} catch (OutOfBoundsException $error) {
	http_response_code(404);
	$result = ['error' => 'Folder not found.'];
} catch (Throwable $error) {
	error_log((string) $error);
	http_response_code(500);
	$result = ['error' => 'Unable to load this folder.'];
}

echo json_encode(
	$result,
	JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR
);
