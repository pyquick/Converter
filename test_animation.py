#!/usr/bin/env python3
"""Test script to verify the animation effects"""

import sys
import time
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from Converter import IconButtonsWindow, run_image_app, run_zip_app

def test_animation():
    app = QApplication(sys.argv)
    
    # Create main window
    window = IconButtonsWindow(q_app=app)
    window.show()
    
    # Test function to simulate button clicks
    def simulate_clicks():
        print("Testing Image Converter animation...")
        run_image_app()
        
        QTimer.singleShot(2000, lambda: print("Testing Archive Manager animation..."))
        QTimer.singleShot(2500, lambda: run_zip_app())
        
        QTimer.singleShot(5000, app.quit)
    
    # Start test after window is shown
    QTimer.singleShot(1000, simulate_clicks)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_animation()