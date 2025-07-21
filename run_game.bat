@echo off
echo Starting Two-Stage Adventure Game...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.x and try again.
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import pygame; import pytmx" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install pygame-ce pytmx
    if errorlevel 1 (
        echo Failed to install packages. Please install manually:
        echo pip install pygame-ce pytmx
        pause
        exit /b 1
    )
)

REM Run the game
echo Starting game...
python start_screen.py

if errorlevel 1 (
    echo Game exited with an error.
    pause
)
