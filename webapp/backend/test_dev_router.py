"""Run: python test_dev_router.py [path-to-php]. Uses temporary files only."""
import http.client
import pathlib
import shutil
import socket
import subprocess
import sys
import tempfile
import time

PHP = sys.argv[1] if len(sys.argv) > 1 else 'php'
ROUTER = pathlib.Path(__file__).with_name('dev-router.php')


def request(port, path, method='GET', headers=None):
	connection = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
	try:
		connection.request(method, path, headers=headers or {})
		response = connection.getresponse()
		return response.status, dict(response.getheaders()), response.read()
	finally:
		connection.close()


def check_server(root, use_router):
	with socket.socket() as sock:
		sock.bind(('127.0.0.1', 0))
		port = sock.getsockname()[1]
	command = [PHP, '-n', '-S', f'127.0.0.1:{port}', '-t', str(root / 'public')]
	if use_router:
		command.append(str(root / 'dev-router.php'))
	with tempfile.TemporaryFile() as log:
		process = subprocess.Popen(command, stdout=log, stderr=log)
		try:
			for _ in range(100):
				if process.poll() is not None:
					log.seek(0)
					raise RuntimeError(log.read().decode(errors='replace'))
				try:
					request(port, '/ping.php')
					break
				except OSError:
					time.sleep(0.05)
			else:
				raise RuntimeError('PHP did not start.')
			if not use_router:
				status, _, body = request(port, '/data/max/clip.mp4', headers={'Range': 'bytes=10-19'})
				print(f'Ordinary PHP server: Range request returned HTTP {status}, {len(body)} bytes.')
				return
			run_checks(port)
		finally:
			process.terminate()
			try:
				process.wait(timeout=5)
			except subprocess.TimeoutExpired:
				process.kill()
				process.wait()


def run_checks(port):
	data = bytes(range(256)) * 4
	cases = [
		('bytes=10-19', 206, data[10:20], 'bytes 10-19/1024'),
		('bytes=1000-', 206, data[1000:], 'bytes 1000-1023/1024'),
		('bytes=-12', 206, data[-12:], 'bytes 1012-1023/1024'),
		('bytes=1000-9999', 206, data[1000:], 'bytes 1000-1023/1024'),
		('bytes=1024-', 416, b'', 'bytes */1024'),
		('bytes=20-10', 416, b'', 'bytes */1024'),
		('bytes=-0', 416, b'', 'bytes */1024'),
		('bytes=0-1,4-5', 200, data, None),
	]
	for value, expected_status, expected_body, expected_range in cases:
		status, headers, body = request(port, '/data/max/clip.mp4', headers={'Range': value})
		assert (status, body) == (expected_status, expected_body), value
		assert headers.get('Content-Range') == expected_range, value
		assert int(headers['Content-Length']) == len(body), value
		assert headers['Accept-Ranges'] == 'bytes', value
	for path in ['/data/max/clip.mp4', '/data/max/space%20%23%20name.mp4']:
		assert request(port, path)[2] == data
	status, headers, body = request(port, '/data/max/clip.mp4', method='HEAD', headers={'Range': 'bytes=1-3'})
	assert status == 200 and body == b'' and headers['Content-Length'] == '1024'
	assert request(port, '/data/max/clip.mp4', method='POST')[0] == 405
	assert request(port, '/data/max/missing.mp4')[0] == 404
	assert request(port, '/data/max/%2e%2e/secret.mp4')[0] == 404
	assert request(port, '/data/max/empty.mp4', headers={'Range': 'bytes=0-'})[0] == 416
	assert request(port, '/data/max/clip.mp4', headers={'Range': 'bytes=1-2', 'If-Range': 'stale'})[0] == 200
	assert request(port, '/ping.php')[2] == b'API OK'
	print('PASS: ranges, exact bytes, HEAD, encoded names, invalid paths, missing files, and PHP fallback.')


def main():
	with tempfile.TemporaryDirectory(prefix='photo-range-test-') as temp:
		root = pathlib.Path(temp)
		media = root / 'public/data/max'
		media.mkdir(parents=True)
		shutil.copyfile(ROUTER, root / 'dev-router.php')
		for name in ['clip.mp4', 'space # name.mp4']:
			(media / name).write_bytes(bytes(range(256)) * 4)
		(media / 'empty.mp4').write_bytes(b'')
		(root / 'public/data/secret.mp4').write_bytes(b'PRIVATE')
		(root / 'public/ping.php').write_text("<?php echo 'API OK';", encoding='utf-8')
		check_server(root, False)
		check_server(root, True)


if __name__ == '__main__':
	main()
