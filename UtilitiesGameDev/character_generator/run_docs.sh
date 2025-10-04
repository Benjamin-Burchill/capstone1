#!/bin/bash

echo "========================================"
echo "Character Generator Documentation Server"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or later"
    exit 1
fi

# Check if Flask is installed
if ! python3 -c "import flask" &> /dev/null; then
    echo "Installing Flask..."
    pip3 install flask markdown
    echo ""
fi

# Run the documentation server
echo "Starting documentation server..."
echo ""
echo "Access documentation at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo "----------------------------------------"
python3 documentation_app.py


