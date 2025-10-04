#!/bin/bash

echo "========================================"
echo "Character Generator Launcher"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or later"
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Found Python $python_version"

# Check if requirements are installed
if ! python3 -c "import PyQt6" &> /dev/null; then
    echo "Installing required packages..."
    pip3 install -r requirements.txt
    echo ""
fi

# Run the GUI application
echo "Starting Character Generator GUI..."
python3 character_gui_simple_3d.py
