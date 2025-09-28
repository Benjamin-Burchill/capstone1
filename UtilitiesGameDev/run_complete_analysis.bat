@echo off
echo =====================================
echo C# Dependency Analyzer and Visualizer
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

echo [Step 1] Running dependency analysis...
echo.
python analyze_csharp_standalone.py --root "..\EoAT_EndofAllThings\Assets\Scripts"

echo.
echo =====================================
echo Analysis complete!
echo.

echo [Step 2] Installing Flask if needed...
python -m pip install flask flask-cors --quiet

echo.
echo [Step 3] Starting visualization server...
echo.
echo The visualization will open in your browser automatically.
echo Press Ctrl+C to stop the server when done.
echo =====================================
echo.

python serve_visualization.py

pause
