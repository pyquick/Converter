#!/usr/bin/env python3
"""Simple test to verify animation dialogs work correctly"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer
from Converter import ImageAppDialog, ZipAppDialog, IconButtonsWindow

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Animation Test")
        self.setGeometry(100, 100, 400, 300)
        
    def test_image_dialog(self):
        print("Testing Image Converter dialog animation...")
        dialog = ImageAppDialog(self)
        dialog.show()
        
    def test_zip_dialog(self):
        print("Testing Archive Manager dialog animation...")
        dialog = ZipAppDialog(self)
        dialog.show()

def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    
    # Test both dialogs with delays
    QTimer.singleShot(1000, window.test_image_dialog)
    QTimer.singleShot(3000, window.test_zip_dialog)
    QTimer.singleShot(6000, app.quit)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()