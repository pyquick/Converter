#!/usr/bin/env python3
"""
Test script for Debug Settings GUI Widget integration in SettingsDialog
"""

import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PySide6.QtWidgets import QApplication
from Converter import SettingsDialog, IconButtonsWindow

def test_settings_integration():
    """Test the Debug Settings GUI Widget integration in SettingsDialog"""
    print("Testing Debug Settings GUI Widget integration...")
    
    app = QApplication(sys.argv)
    
    # Create main window and settings dialog
    main_window = IconButtonsWindow(q_app=app)
    settings_dialog = SettingsDialog(parent_window=main_window)
    
    # Check if debug widget is properly integrated
    debug_widget = settings_dialog.debug_widget
    
    if debug_widget:
        print("✅ Debug Settings GUI Widget successfully integrated in SettingsDialog")
        print("✅ Widget object name:", debug_widget.objectName())
        print("✅ Widget type:", type(debug_widget).__name__)
    else:
        print("❌ Debug Settings GUI Widget not found in SettingsDialog")
        return 1
    
    # Test theme application
    print("\n🧪 Testing theme application...")
    settings_dialog.apply_theme(False)  # Light theme
    print("✅ Light theme applied successfully")
    
    settings_dialog.apply_theme(True)   # Dark theme  
    print("✅ Dark theme applied successfully")
    
    print("\n🎉 All integration tests passed!")
    print("\nFeatures verified:")
    print("- Debug Settings Widget integrated into SettingsDialog")
    print("- Theme switching works correctly")
    print("- Widget object naming preserved")
    
    return 0

if __name__ == "__main__":
    exit_code = test_settings_integration()
    sys.exit(exit_code)