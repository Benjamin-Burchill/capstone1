#!/bin/bash

# Quick Start script for OBJ to Sprite Converter on Linux/Mac

echo "========================================"
echo "  OBJ to Sprite Converter - Quick Start"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from python.org"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
    echo
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing required packages..."
pip install -q -r requirements.txt
echo

# Function to show menu
show_menu() {
    echo "========================================"
    echo "  Select an option:"
    echo "========================================"
    echo "  1. Test converter with sample models"
    echo "  2. Convert a single OBJ file"
    echo "  3. Batch convert directory"
    echo "  4. Run advanced tests"
    echo "  5. View documentation"
    echo "  6. Exit"
    echo "========================================"
}

# Main loop
while true; do
    show_menu
    read -p "Enter your choice (1-6): " choice
    
    case $choice in
        1)
            echo
            echo "Running test converter..."
            python test_converter.py
            echo
            read -p "Press Enter to continue..."
            ;;
        2)
            echo
            read -p "Enter OBJ file path: " objfile
            read -p "Enter number of directions (6 or 8) [6]: " dirs
            dirs=${dirs:-6}
            read -p "Enter sprite size [128]: " size
            size=${size:-128}
            
            echo "Converting $objfile..."
            python obj_to_sprites.py "$objfile" -d $dirs -s $size
            echo
            read -p "Press Enter to continue..."
            ;;
        3)
            echo
            read -p "Enter directory containing OBJ files: " batchdir
            read -p "Enter category (units/heroes/buildings) [units]: " category
            category=${category:-units}
            
            echo "Batch converting directory $batchdir..."
            python batch_convert.py "$batchdir" -c $category
            echo
            read -p "Press Enter to continue..."
            ;;
        4)
            echo
            echo "Running advanced tests..."
            python test_converter.py --advanced
            echo
            read -p "Press Enter to continue..."
            ;;
        5)
            echo
            echo "Showing documentation..."
            less README.md
            echo
            read -p "Press Enter to continue..."
            ;;
        6)
            echo
            echo "Thank you for using OBJ to Sprite Converter!"
            deactivate
            exit 0
            ;;
        *)
            echo "Invalid choice. Please try again."
            echo
            ;;
    esac
done
