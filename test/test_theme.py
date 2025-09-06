#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from con import CON
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
import launcher

def check_theme():
    print(f"CON.theme_system value: {CON.theme_system}")

if __name__ == "__main__":
    # Create QApplication instance
    app = QApplication(sys.argv)
    
    # Create window
    window = launcher.IconButtonsWindow(q_app=app)
    
    # Check theme after window is created
    QTimer.singleShot(1000, check_theme)
    
    # Show window and run app
    window.show()
    
    # Exit after 3 seconds
    QTimer.singleShot(3000, app.quit)
    
    sys.exit(app.exec())