#!/usr/bin/env python3

"""
Test script for verifying success overlay theme switching
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from qfluentwidgets import setTheme, Theme

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui_converter import ICNSConverterGUI


def test_theme_switching():
    """Test success overlay theme switching"""
    app = QApplication(sys.argv)
    
    # Set initial theme
    setTheme(Theme.AUTO)
    
    # Create main window
    window = ICNSConverterGUI()
    window.show()
    
    # Show success view
    window.show_success_view()
    
    # Print initial theme
    print("Initial theme applied")
    
    # Schedule theme switch to dark after 3 seconds
    def switch_to_dark():
        print("Switching to dark theme")
        setTheme(Theme.DARK)
        window._apply_theme(True)
    
    QTimer.singleShot(3000, switch_to_dark)
    
    # Schedule theme switch to light after 6 seconds
    def switch_to_light():
        print("Switching to light theme")
        setTheme(Theme.LIGHT)
        window._apply_theme(False)
    
    QTimer.singleShot(6000, switch_to_light)
    
    # Schedule exit after 9 seconds
    def exit_app():
        print("Exiting test")
        app.quit()
    
    QTimer.singleShot(9000, exit_app)
    
    print("Test window displayed. Observe success overlay theme changes.")
    print("The window will automatically close after 9 seconds.")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_theme_switching()