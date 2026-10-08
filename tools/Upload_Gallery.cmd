@echo off
setlocal DisableDelayedExpansion

rem Place in tools, beside .venv-photos and photo-tools.
set "PHOTO_PYTHON=%~dp0.venv-photos\Scripts\python.exe"
set "PHOTO_UPLOAD=%~dp0photo-tools\upload_gallery.py"
set "PHOTO_EXIT_CODE=1"

if not exist "%PHOTO_PYTHON%" (
	echo Python environment not found: "%PHOTO_PYTHON%"
	goto finish
)

if not exist "%PHOTO_UPLOAD%" (
	echo Upload script not found: "%PHOTO_UPLOAD%"
	goto finish
)

"%PHOTO_PYTHON%" -X utf8 -u "%PHOTO_UPLOAD%" %*
set "PHOTO_EXIT_CODE=%ERRORLEVEL%"

:finish
echo.
if "%PHOTO_EXIT_CODE%"=="0" (
	echo Command completed.
) else (
	echo Upload command did not complete. See the messages above.
)
pause
exit /b %PHOTO_EXIT_CODE%
