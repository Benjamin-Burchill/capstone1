@echo off
REM Quick Start script for OBJ to Sprite Converter on Windows

echo ========================================
echo   OBJ to Sprite Converter - Quick Start
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing required packages...
pip install -q -r requirements.txt
echo.

REM Menu
:menu
echo ========================================
echo   Select an option:
echo ========================================
echo   1. Test converter with sample models
echo   2. Convert a single OBJ file
echo   3. Batch convert directory
echo   4. Run advanced tests
echo   5. View documentation
echo   6. Exit
echo ========================================
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto test
if "%choice%"=="2" goto single
if "%choice%"=="3" goto batch
if "%choice%"=="4" goto advanced
if "%choice%"=="5" goto docs
if "%choice%"=="6" goto end

echo Invalid choice. Please try again.
echo.
goto menu

:test
echo.
echo Running test converter...
python test_converter.py
echo.
pause
goto menu

:single
echo.
set /p objfile="Enter OBJ file path: "
set /p dirs="Enter number of directions (6 or 8) [6]: "
if "%dirs%"=="" set dirs=6
set /p size="Enter sprite size [128]: "
if "%size%"=="" set size=128

echo Converting %objfile%...
python obj_to_sprites.py "%objfile%" -d %dirs% -s %size%
echo.
pause
goto menu

:batch
echo.
set /p batchdir="Enter directory containing OBJ files: "
set /p category="Enter category (units/heroes/buildings) [units]: "
if "%category%"=="" set category=units

echo Batch converting directory %batchdir%...
python batch_convert.py "%batchdir%" -c %category%
echo.
pause
goto menu

:advanced
echo.
echo Running advanced tests...
python test_converter.py --advanced
echo.
pause
goto menu

:docs
echo.
echo Opening documentation...
type README.md | more
echo.
pause
goto menu

:end
echo.
echo Thank you for using OBJ to Sprite Converter!
deactivate
pause
