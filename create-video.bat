@echo off
REM
REM ╔════════════════════════════════════════════════════════════════╗
REM ║      🎬 ONE COMMAND VIDEO CREATOR                            ║
REM ║      Tạo video chỉ với 1 lệnh duy nhất!                     ║
REM ╚════════════════════════════════════════════════════════════════╝
REM
REM Usage:
REM   create-video.bat              (Default - Vietnamese)
REM   create-video.bat en           (English)
REM   create-video.bat quick        (Quick mode)
REM

setlocal enabledelayedexpansion

cls

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║      ✨ ULTIMATE YOUTUBE VIDEO CREATOR ✨                    ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is available
where python >nul 2>nul
if errorlevel 1 (
    color 0C
    echo.
    echo ❌ Python is not installed or not in PATH!
    echo.
    echo Please install Python from: https://www.python.org/
    echo.
    pause
    exit /b 1
)

REM Run the Python script with arguments
python create_video.py %*

REM Preserve exit code
exit /b %ERRORLEVEL%
