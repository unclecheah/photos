@echo off
setlocal DisableDelayedExpansion

rem Place this launcher in tools, beside .venv-photos and photo-tools.
set "PHOTO_PYTHON=%~dp0.venv-photos\Scripts\python.exe"
set "PHOTO_SCRIPT=%~dp0photo-tools\prepare_gallery.py"
set "PHOTO_CONFIG=%~dp0photo-tools\gallery-config.json"
set "PHOTO_EXIT_CODE=1"

if not exist "%PHOTO_PYTHON%" (
	echo Python environment not found: "%PHOTO_PYTHON%"
	echo Check that .venv-photos is inside tools.
	goto finish
)

if not exist "%PHOTO_SCRIPT%" (
	echo Preparation script not found: "%PHOTO_SCRIPT%"
	echo Check that photo-tools is inside tools.
	goto finish
)

"%PHOTO_PYTHON%" -X utf8 -u "%PHOTO_SCRIPT%" --config "%PHOTO_CONFIG%" %*
set "PHOTO_EXIT_CODE=%ERRORLEVEL%"

:finish
echo.
if "%PHOTO_EXIT_CODE%"=="0" (
	echo Gallery preparation completed.
) else (
	echo Gallery preparation failed. See the messages above.
)
pause
exit /b %PHOTO_EXIT_CODE%
