@echo off
echo =====================================
echo C# Dependency Visualizer
echo =====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.x from python.org
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements_dependency_viz.txt
    echo.
)

REM Run the visualizer
echo Starting C# Dependency Visualizer...
echo.
echo The visualizer will analyze your C# scripts and open in your browser.
echo Press Ctrl+C to stop the server when done.
echo.
echo =====================================
echo.

python csharp_dependency_visualizer.py --root "..\EoAT_EndofAllThings"

pause
