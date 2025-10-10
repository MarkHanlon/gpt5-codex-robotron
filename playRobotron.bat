@echo off
setlocal

REM Move to the directory containing this script so relative paths resolve.
cd /d "%~dp0"

echo Installing Python dependencies...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt || goto :error

echo.
echo Launching Robotron Remix!
python -m robotron_remix.main
goto :eof

:error
echo.
echo Installation failed. Please review the messages above.
pause
