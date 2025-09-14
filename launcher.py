# -*- coding: utf-8 -*-

from concurrent.futures import thread
from importlib import reload
import sys
import os
import threading
import time
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpacerItem,
    QGridLayout,
    QSizePolicy,
    QDialog, # Import QDialog for settings window
    QComboBox, # For theme selection dropdown
    QGroupBox, # For update settings group
    QTabWidget, # For tabbed settings interface
    QStackedWidget # For segmented widget interface
)
from PySide6.QtGui import QIcon, QPainter, QPixmap, QPalette
from PySide6.QtCore import QSize, Qt, QSettings, QPropertyAnimation, QEasingCurve, QMetaObject, Q_ARG, Signal, Slot # Import QPropertyAnimation and QEasingCurve for animations
import multiprocessing
from qfluentwidgets import Theme, setTheme, CheckBox, SegmentedWidget
 # Keep for freeze_support, but remove direct Process usage
from settings.update_settings_gui import UpdateDialog
from con import CON # Import CON instance for theme settings
# Encoding settings have been moved to debug_logger for handling
# --- Helper function to create placeholder icons ---
# Since we cannot directly generate .icns files, we create PNG files as examples.
# Please place the AppIcon.icns and zip.icns files in the same directory as this script.
def create_placeholder_icon(path: str, color: str, text: str):
    """Create a simple PNG placeholder icon if the icon file does not exist."""
    if not os.path.exists(path):
        pixmap = QPixmap(128, 128)
        pixmap.fill(color)
        painter = QPainter(pixmap)
        painter.setPen("white")
        font = painter.font()
        font.setPointSize(48)
        
        painter.setFont(font)
        # Qt.AlignCenter is enum value 1
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
        painter.end()
        pixmap.save(path)
        print(f"Note: '{path}' not found. A placeholder icon has been created.")
        return True
    # If it's an .icns file, use it directly
    elif path.endswith(".icns") and os.path.exists(path):
        return True
    # If a non-.icns placeholder file exists, consider it successful
    elif not path.endswith(".icns") and os.path.exists(path):
        return True
    return False

class IconButtonsWindow(QWidget):
    
    def _load_qss_file(self, filename):
        """Load QSS content from external file"""
        qss_path = os.path.join(os.path.dirname(__file__), 'qss', filename)
        try:
            with open(qss_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: QSS file not found: {qss_path}")
            return ""
        except Exception as e:
            print(f"Error loading QSS file {qss_path}: {e}")
            return ""

    @property
    def LIGHT_QSS(self):
        """Load light theme QSS from external file"""
        return self._load_qss_file('launcher_light.qss')

    @property
    def DARK_QSS(self):
        """Load dark theme QSS from external file"""
        return self._load_qss_file('launcher_dark.qss')

    
    def __init__(self, q_app: QApplication):
        super().__init__()
        self._q_app = q_app # Store QApplication instance
        self.setWindowTitle("Converter")
        # Load theme setting immediately
        self.settings = QSettings("MyCompany", "ConverterApp")
        self.theme_setting = self.settings.value("theme", 0, type=int)

        self.path= os.path.dirname(os.path.abspath(__file__))
        # Define paths for icon files
        self.app_icon_path = os.path.join(self.path,"AppIcon.png")
        self.appd_icon_path = os.path.join(self.path,"AppIcond.png")
        self.zip_icon_path = os.path.join(self.path,"zip.png")
        self.zipd_icon_path = os.path.join(self.path,"zipd.png")

        # Check if icon files exist and create placeholders if needed
        if not os.path.exists(self.app_icon_path):
            print("Note: AppIcon.png file not found. Will try to create a PNG placeholder icon.")
            create_placeholder_icon(self.app_icon_path, "dodgerblue", "App")
        if not os.path.exists(self.appd_icon_path):
            print("Note: AppIcond.png file not found. Will try to create a PNG placeholder icon.")
            create_placeholder_icon(self.appd_icon_path, "darkblue", "AppD") # Changed placeholder color for dark mode app icon
        
        if not os.path.exists(self.zip_icon_path):
            print("Note: zip.png file not found. Will try to create a PNG placeholder icon.")
            create_placeholder_icon(self.zip_icon_path, "gray", "Zip")

        if not os.path.exists(self.zipd_icon_path):
            print("Note: zipd.png file not found. Will try to create a PNG placeholder icon.")
            create_placeholder_icon(self.zipd_icon_path, "dimgray", "ZipD")

        self.init_ui()
        # Apply theme based on settings or initial system detection
        self._apply_system_theme_from_settings() 
    
    def _apply_system_theme(self, is_dark_mode): # This method will now be primarily for paletteChanged signal
        # Only apply system theme if setting is System Default
        if self.settings.value("theme", 0, type=int) == 0:
            self._apply_theme(is_dark_mode)

    def _apply_system_theme_from_settings(self):
        theme_setting = self.settings.value("theme", 0, type=int)
        if self._q_app:
            if theme_setting == 0: # System Default
                is_dark_mode = self._q_app.palette().color(QPalette.ColorRole.Window).lightnessF() < 0.5
                self._apply_theme(is_dark_mode)
            elif theme_setting == 1: # Light Mode
                # 强制应用浅色主题，不依赖系统主题
                self._apply_theme(False)
            else: # Dark Mode
                # 强制应用深色主题，不依赖系统主题
                self._apply_theme(True)
        # Removed else block for print statement, as it's a development warning

    def _apply_theme(self, is_dark_mode):
        if is_dark_mode:
            self.setStyleSheet(self.DARK_QSS)
            if hasattr(self, 'button_zip'):
                self.button_zip.setIcon(QIcon(self.zipd_icon_path))
            if hasattr(self, 'button_app'):
                self.button_app.setIcon(QIcon(self.appd_icon_path))
        else:
            self.setStyleSheet(self.LIGHT_QSS)
            if hasattr(self, 'button_zip'):
                self.button_zip.setIcon(QIcon(self.zip_icon_path))
            if hasattr(self, 'button_app'):
                self.button_app.setIcon(QIcon(self.app_icon_path))
        
        # Notify all sub-widgets to update theme
        self.update_sub_widgets_theme(is_dark_mode)
    
    def update_sub_widgets_theme(self, is_dark_mode):
        """Notify all sub-widgets to update theme"""
        # Update settings dialog theme (if already created)
        if hasattr(self, '_settings_dialog') and self._settings_dialog:
            self._settings_dialog.apply_theme(is_dark_mode)
    
    def init_ui(self):
        # Create main layout
        main_layout = QVBoxLayout()
        
        main_layout.setSpacing(30)  # Increased spacing for better visual separation
        main_layout.setContentsMargins(40, 40, 40, 40)  # Increased margins for more breathing room
        
        # Add title
        title_label = QLabel("Converter")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # --- Button 1: AppIcon ---
        app_icon = QIcon(self.app_icon_path)
        self.button_app = QPushButton(" Image Converter")
        self.button_app.setObjectName("button_app")
        self.button_app.setIcon(app_icon)
        self.button_app.setIconSize(QSize(72, 72))  # Increased icon size
        self.button_app.setMinimumHeight(90)  # Increased minimum height
        self.button_app.clicked.connect(run_image_app)

        # --- Button 2: zip.icns ---
        zip_icon = QIcon(self.zip_icon_path)
        self.button_zip = QPushButton(" Archive Converter")  # Removed extra space
        self.button_zip.setObjectName("button_zip")
        self.button_zip.setIcon(zip_icon)
        self.button_zip.setIconSize(QSize(72,72))  # Increased icon size
        self.button_zip.setMinimumHeight(90)  # Increased minimum height
        self.button_zip.clicked.connect(run_zip_app)

        # Create horizontal layouts to center buttons
        app_button_layout = QHBoxLayout()
        app_button_layout.addStretch()
        app_button_layout.addWidget(self.button_app)
        app_button_layout.addStretch()
        
        zip_button_layout = QHBoxLayout()
        zip_button_layout.addStretch()
        zip_button_layout.addWidget(self.button_zip)
        zip_button_layout.addStretch()

        # Add buttons to layout
        main_layout.addLayout(app_button_layout)
        main_layout.addLayout(zip_button_layout)
        
        # Add vertical space
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Settings button - positioned below zip button
        settings_button = QPushButton(QIcon.fromTheme("preferences-system"), " Settings")  # Added text to button
        settings_button.setObjectName("settings_button")
        settings_button.setIconSize(QSize(28, 28))  # Increased icon size
        settings_button.setFixedSize(140, 45)  # Increased size for better touch target
        settings_button.clicked.connect(self.show_settings)
        settings_button.setStyleSheet("""
            #settings_button {
                background-color: #607D8B;
                border: none;
                color: white;
                padding: 6px 20px;
                text-align: center;
                font-size: 15px;
                margin: 6px 0;
                border-radius: 16px;
                font-weight: bold;
   
   
            }
            #settings_button:hover {
                background-color: #455A64;
   
            }
            #settings_button:pressed {
                background-color: #263238;
   
   
            }
        """)

        settings_button_layout = QHBoxLayout()
        settings_button_layout.addStretch()
        settings_button_layout.addWidget(settings_button)
        settings_button_layout.addStretch()
        main_layout.addLayout(settings_button_layout)

        # Set the main layout for the window
        self.setLayout(main_layout)

    def show_settings(self):
        settings_dialog = SettingsDialog(self)
        self._settings_dialog = settings_dialog  # Save dialog reference
        settings_dialog.show() # Use show() instead of exec() to keep dialog non-modal

def run_zip():
    from zip_gui import ZipAppRunner
    app_runner = ZipAppRunner()
    app_runner.MainLoop()
def run_image():
    from gui_converter import ICNSConverterApp
    app_runner = ICNSConverterApp()
    app_runner.MainLoop()
def run_zip_app():
    multiprocessing.Process(target=run_zip).start()
def run_image_app():
    multiprocessing.Process(target=run_image).start()



# --- Settings Dialog Class ---
class SettingsDialog(QDialog):
    # Define signal for inter-thread communication
    update_status_signal = Signal(str, bool)
    
    def __init__(self, parent_window: IconButtonsWindow):
        super().__init__(parent_window)
        self.parent_window = parent_window # Store reference to the main window
        self.setWindowTitle("Settings")
                #self.setFixedSize(800, 600) # Increased size for better aesthetics and more content
        
        # Connect signals
        self.update_status_signal.connect(self._update_status_label)
        
        self.init_ui()
        self.load_settings()
        self._apply_theme_from_parent() # Apply theme based on parent's current theme
        self._connect_settings_signals() # Connect settings signals for real-time saving

        # Animation for showing the dialog
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(250) # Duration in milliseconds
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def showEvent(self, event):
        # Start animation when the dialog is shown
        self.animation.start()
        super().showEvent(event)

    def _apply_theme_from_parent(self):
        if self.parent_window:
            # Get parent window's theme setting instead of judging by system palette
            theme_setting = self.parent_window.settings.value("theme", 0, type=int)
            if theme_setting == 0: # System Default
                # Only use system palette when System Default is selected
                is_dark_mode = self.parent_window.palette().color(QPalette.ColorRole.Window).lightnessF() < 0.5
                self.apply_theme(is_dark_mode)
            elif theme_setting == 1: # Light Mode
                self.apply_theme(False)
            else: # Dark Mode
                self.apply_theme(True)
    def _load_settings_qss_file(self, filename):
        """Load QSS content from external settings file"""
        qss_path = os.path.join(os.path.dirname(__file__), 'qss', filename)
        try:
            with open(qss_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: Settings QSS file not found: {qss_path}")
            return ""
        except Exception as e:
            print(f"Error loading settings QSS file {qss_path}: {e}")
            return ""

    @property
    def SETTINGS_LIGHT_QSS(self):
        """Load light theme QSS from external file"""
        return self._load_settings_qss_file('settings_light.qss')

    @property
    def SETTINGS_DARK_QSS(self):
        """Load dark theme QSS from external file"""
        return self._load_settings_qss_file('settings_dark.qss')

    def apply_theme(self, is_dark_mode):
        if is_dark_mode:
            self.setStyleSheet(self.SETTINGS_DARK_QSS)
        else:
            self.setStyleSheet(self.SETTINGS_LIGHT_QSS)

    def init_ui(self):
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Create SegmentedWidget and QStackedWidget
        self.segmented_widget = SegmentedWidget(self)
        self.stacked_widget = QStackedWidget(self)
        
        # Debug page
        debug_page = QWidget()
        debug_layout = QVBoxLayout(debug_page)
        debug_layout.setContentsMargins(15, 15, 15, 15)
        debug_layout.setSpacing(15)
        
        from debug.debug_gui import DebugSettingsWidget
        self.debug_widget = DebugSettingsWidget()
        self.debug_widget.setObjectName("debug_widget")
        debug_layout.addWidget(self.debug_widget)
        debug_layout.addStretch()
        
        self.stacked_widget.addWidget(debug_page)
        
        # Update page
        update_page = QWidget()
        update_layout = QVBoxLayout(update_page)
        update_layout.setContentsMargins(15, 15, 15, 15)
        update_layout.setSpacing(15)
        
        self.update_group = UpdateDialog()
        self.update_group.setObjectName("update_group")
        update_layout.addWidget(self.update_group)
        update_layout.addStretch()
        
        self.stacked_widget.addWidget(update_page)
        
        # Image Converter page
        image_converter_page = QWidget()
        image_converter_layout = QVBoxLayout(image_converter_page)
        image_converter_layout.setContentsMargins(15, 15, 15, 15)
        image_converter_layout.setSpacing(15)
        
        from settings.image_converter_settings import ImageConverterSettingsWidget
        self.image_converter_widget = ImageConverterSettingsWidget()
        self.image_converter_widget.setObjectName("image_converter_widget")
        image_converter_layout.addWidget(self.image_converter_widget)
        image_converter_layout.addStretch()
        
        self.stacked_widget.addWidget(image_converter_page)
        
        # Add tab items
        self.add_sub_interface(debug_page, "debug_page", "Debug")
        self.add_sub_interface(update_page, "update_page", "Update")
        self.add_sub_interface(image_converter_page, "image_converter_page", "Image Converter")
        
        # Connect signals and initialize current page
        self.stacked_widget.currentChanged.connect(self.on_current_index_changed)
        self.stacked_widget.setCurrentIndex(0)
        self.segmented_widget.setCurrentItem("debug_page")
        
        # Add to main layout
        main_layout.addWidget(self.segmented_widget, 0, Qt.AlignmentFlag.AlignHCenter)
        main_layout.addWidget(self.stacked_widget)

        # Real-time auto-save status label
        self.status_label = QLabel("Settings automatically saved")
        self.status_label.setObjectName("status_label")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.status_label.setVisible(False)
        
        status_layout = QHBoxLayout()
        status_layout.addStretch()
        status_layout.addWidget(self.status_label)
        main_layout.addLayout(status_layout)

    def add_sub_interface(self, widget: QWidget, object_name: str, text: str):
        """Add sub-page to SegmentedWidget and QStackedWidget"""
        widget.setObjectName(object_name)
        self.segmented_widget.addItem(
            routeKey=object_name,
            text=text,
            onClick=lambda: self.stacked_widget.setCurrentWidget(widget)
        )

    def on_current_index_changed(self, index):
        """Handle current page change"""
        widget = self.stacked_widget.widget(index)
        if widget:
            self.segmented_widget.setCurrentItem(widget.objectName())

    def load_settings(self):
        settings = QSettings("MyCompany", "ConverterApp")
        # Theme settings - always set to System Default (index 0)
        settings.setValue("theme", 0) # Force save System Default
        
        # Debug settings are now handled by the DebugSettingsWidget itself
        
        # Load Image Converter settings
        if hasattr(self, 'image_converter_widget'):
            self.image_converter_widget.load_settings()



    def _connect_settings_signals(self):
        """Connect all settings controls' signals to real-time saving"""
        # Connect debug widget auto-save signals (already handled in DebugSettingsWidget)
        # Debug settings are now handled by the DebugSettingsWidget itself
        
        # Connect update dialog settings
        if hasattr(self, 'update_group') and hasattr(self.update_group, 'include_prerelease_checkbox'):
            self.update_group.include_prerelease_checkbox.stateChanged.connect(self.on_settings_changed)
        
        # Connect image converter settings
        if hasattr(self, 'image_converter_widget'):
            self.image_converter_widget.settings_changed.connect(self.on_settings_changed)
            # Also notify any open image converter windows about settings changes
            self.image_converter_widget.settings_changed.connect(self._notify_image_converter_settings_changed)
        
        # Connect theme settings from parent window if available
        if self.parent_window and hasattr(self.parent_window, 'settings'):
            # Theme changes are handled by the parent window's auto-save mechanism
            pass
    
    def on_settings_changed(self):
        """Handle any settings change and trigger auto-save"""
        self.save_settings_async()
    
    @Slot(str, bool)
    def _update_status_label(self, text, visible):
        """Safe update status label slot function"""
        self.status_label.setText(text)
        self.status_label.setVisible(visible)
    
    def _notify_image_converter_settings_changed(self):
        """Notify any open image converter windows about settings changes"""
        # This method can be used to notify image converter instances
        # about settings changes if needed in the future
        pass
    
    def save_settings_async(self):
        """Asynchronously save settings in a separate thread"""
        def save_thread():
            settings = QSettings("MyCompany", "ConverterApp")
            # Theme settings - always System Default
            settings.setValue("theme", 0)
            
            # Debug settings are now handled by the DebugSettingsWidget itself
            
            # Save image converter settings
            if hasattr(self, 'image_converter_widget'):
                self.image_converter_widget.save_settings()
            
            settings.sync() # Ensure settings are written to disk
            
            # Safely update UI in main thread via signal
            #self.update_status_signal.emit("Settings saved", True)
            
            # Hide status label after 2 seconds
            time.sleep(2)
            self.update_status_signal.emit("", False)
        
        # Start separate thread to execute save operation
        thread = threading.Thread(target=save_thread)
        thread.daemon = True
        thread.start()
        
        # Apply theme changes immediately
        if self.parent_window:
            self.parent_window._apply_system_theme_from_settings()
    
    def accept(self):
        """Override accept method to save settings without closing dialog"""
        self.save_settings_async()
    
    def reject(self):
        """Override reject method to save settings and close dialog"""
        self.save_settings_async()
        super().reject()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    
    # Initialize debug logger
    try:
        from support.debug_logger import debug_logger
        debug_logger.setup_logger()
        if debug_logger.is_debug_enabled():
            print("Debug mode enabled - logging to ~/.converter/log")
    except Exception as e:
        print(f"Failed to initialize debug logger: {e}")
    
    from support.toggle import theme_manager
    theme_manager.start()
    setTheme(Theme.AUTO)
    window = IconButtonsWindow(q_app=app)
    window.show()
    # Connect to palette changes for real-time theme switching ONLY if setting is System Default
    app.paletteChanged.connect(lambda: window._apply_system_theme(app.palette().color(QPalette.ColorRole.Window).lightnessF() < 0.5))
    exit_code = app.exec()
    
    # Cleanup debug logger
    try:
        from support.debug_logger import debug_logger
        debug_logger.restore_output()
    except:
        pass
    
    theme_manager.stop()
    sys.exit(exit_code)