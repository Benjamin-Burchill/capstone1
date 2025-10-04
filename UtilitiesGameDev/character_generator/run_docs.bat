@echo off
echo ========================================
echo Character Generator Documentation Server
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

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing Flask...
    pip install flask markdown
    echo.
)

REM Run the documentation server
echo Starting documentation server...
echo.
echo Access documentation at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo ----------------------------------------
python documentation_app.py

pause


