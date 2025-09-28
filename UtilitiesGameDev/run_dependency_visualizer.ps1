# C# Dependency Visualizer PowerShell Script

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "C# Dependency Visualizer" -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.x from python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check and install dependencies
Write-Host "Checking dependencies..." -ForegroundColor Cyan
$flaskInstalled = pip show flask 2>&1 | Select-String "Name: flask"
if (-not $flaskInstalled) {
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    pip install -r requirements_dependency_viz.txt
    Write-Host ""
}

# Run the visualizer
Write-Host "Starting C# Dependency Visualizer..." -ForegroundColor Green
Write-Host ""
Write-Host "The visualizer will analyze your C# scripts and open in your browser." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server when done." -ForegroundColor Yellow
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Run with parameters
$params = @()
if ($args.Count -gt 0) {
    $params = $args
} else {
    $params = @("--root", "..\EoAT_EndofAllThings")
}

python csharp_dependency_visualizer.py @params
