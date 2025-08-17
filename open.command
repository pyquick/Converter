#!/bin/bash

# Simple launcher script for PNG to ICNS Converter
# This script can be used as an alternative to a compiled .app bundle

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Run the Python application
echo "Starting PNG to ICNS Converter..."
echo "If you get a 'module not found' error, please install Pillow:"
echo "pip3 install Pillow"
echo ""

python3 gui_converter.py

# Check if the command was successful
if [ $? -eq 0 ]; then
    echo "Application closed successfully."
else
    echo "Application failed to start."
    echo "Please make sure you have Python 3 and Pillow installed:"
    echo "pip3 install Pillow"
    echo ""
    echo "Press any key to exit..."
    read -n 1 -s
fi