#!/usr/bin/env python3
"""
Test script for Debug Settings GUI Widget
"""

import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PySide6.QtWidgets import QApplication
from debug.debug_gui import DebugSettingsWidget

def test_debug_gui():
    """Test the Debug Settings GUI Widget"""
    print("Testing Debug Settings GUI Widget...")
    
    app = QApplication(sys.argv)
    
    # Create and show the debug settings widget
    widget = DebugSettingsWidget()
    widget.setWindowTitle("Debug Settings Test")
    widget.resize(800, 600)
    widget.show()
    
    print("Debug Settings GUI Widget created successfully!")
    print("Features available:")
    print("- Enable/Disable Debug Mode")
    print("- Enable/Disable Enhanced Logging")
    print("- Test Debug Output button")
    print("- View Log Directory button")
    print("- Clear Logs button")
    print("- Real-time status updates")
    print("- Log preview area")
    
    return app.exec()

if __name__ == "__main__":
    exit_code = test_debug_gui()
    sys.exit(exit_code)