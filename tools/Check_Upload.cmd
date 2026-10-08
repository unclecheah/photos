@echo off
setlocal DisableDelayedExpansion

rem Place this launcher in tools, beside .venv-photos and photo-tools.
set "PHOTO_PYTHON=%~dp0.venv-photos\Scripts\python.exe"
set "PHOTO_CHECK=%~dp0photo-tools\check_upload_connection.py"
set "PHOTO_EXIT_CODE=1"

if not exist "%PHOTO_PYTHON%" (
	echo Python environment not found: "%PHOTO_PYTHON%"
	goto finish
)

if not exist "%PHOTO_CHECK%" (
	echo Connection-check script not found: "%PHOTO_CHECK%"
	goto finish
)

"%PHOTO_PYTHON%" -X utf8 -u "%PHOTO_CHECK%" %*
set "PHOTO_EXIT_CODE=%ERRORLEVEL%"

:finish
echo.
if "%PHOTO_EXIT_CODE%"=="0" (
	echo FTP connection check completed.
) else (
	echo FTP connection check did not complete. See the messages above.
)
pause
exit /b %PHOTO_EXIT_CODE%
