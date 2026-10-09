# Local video seeking fix

The gallery diagnostic reported a duration of 85.9 seconds but a seekable range of [0, 0]. Programmatic seeking also restarted playback. This points to media delivery rather than the native timeline controls. The ordinary PHP 8.3 development server was verified to ignore a byte-range request; the included router supplies byte-range responses for videos.

## Install

1. Extract this ZIP into `webapp`. It adds `backend/dev-router.php` and `backend/test_dev_router.py`.
2. Stop the running PHP server with Ctrl+C.
3. From `webapp/backend`, run:

```bash
php -S 127.0.0.1:8080 -t public dev-router.php
```

4. Keep Vite running. Its `/api/` and `/data/` proxy targets should point to `http://127.0.0.1:8080` (the value in the previously supplied updated Vite config). If you edit those targets, restart Vite.
5. Close the video viewer, hard-refresh the gallery with Ctrl+F5, reopen the video and try the timeline.

This follows the established layout: media files are under `backend/public/data/max`; APIs are under `backend/public/api`. The router resolves its media directory relative to its own location. No media conversion or reupload is needed for this change.

Remove the temporary `display: none !important` rule for the loading overlay if you added it. The existing overlay's non-blocking mode is suitable for the viewer. The earlier JavaScript gesture patch can remain, but it does not fix missing byte-range responses.

## How it works

Video URLs and frontend code stay the same. PHP receives the video request and returns HTTP 206 with the requested byte range. Ordinary requests get the full file. Other requests fall through to PHP's normal development server, including execution of your existing API endpoints.

Supported video filename extensions: mp4, m4v, webm, ogv, mov. This controls delivery only; the video codec must still be supported by the browser.

## Repeatable verification

Requires PHP 8.1+ and Python 3. From `webapp/backend`:

```bash
python test_dev_router.py
```

Or pass your PHP executable:

```bash
python test_dev_router.py "C:\xampp\php\php.exe"
```

The test uses a temporary directory and a separate free port. It does not modify your media or contact your hosting account. It checks partial content and exact returned bytes, suffix/open-ended ranges, HEAD, invalid ranges, encoded filenames, traversal rejection, and PHP API fallback.

For a real video, run in Windows CMD (replace the filename with your own URL-encoded path):

```bat
curl.exe -sS -D - -o NUL -H "Range: bytes=0-1023" "http://localhost:3000/data/max/your-video.mp4"
```

Expected for a video larger than 1024 bytes: `206 Partial Content`, `Accept-Ranges: bytes`, `Content-Range: bytes 0-1023/TOTAL`, and `Content-Length: 1024`.

## Scope

This router is for `php -S` during local development. On the hosted site, the web server should handle static video range requests; do not change production routing based on this local fix. The user's actual server headers have not been captured yet, so verify through the gallery URL if the issue remains.
