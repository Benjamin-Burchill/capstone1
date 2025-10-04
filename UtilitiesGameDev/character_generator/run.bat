@echo off
echo ========================================
echo Character Generator Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later
    pause
    exit /b 1
)

REM Check if requirements are installed
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    echo.
)

REM Run the GUI application
echo Starting Character Generator GUI...
python character_gui_simple_3d.py

pause
