from concurrent.futures import thread
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
    QGroupBox # For update settings group
)
from PySide6.QtGui import QIcon, QPainter, QPixmap, QPalette
from PySide6.QtCore import QSize, Qt, QSettings, QPropertyAnimation, QEasingCurve, QMetaObject, Q_ARG, Signal, Slot # Import QPropertyAnimation and QEasingCurve for animations
import multiprocessing

from qfluentwidgets import Theme, setTheme # Keep for freeze_support, but remove direct Process usage
from update.update_gui import UpdateDialog
from con import CON # Import CON instance for theme settings

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
        
        # 通知所有子控件更新主题
        self.update_sub_widgets_theme(is_dark_mode)
    
    def update_sub_widgets_theme(self, is_dark_mode):
        """通知所有子控件更新主题"""
        # 更新设置对话框的主题（如果已创建）
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
        self.button_zip = QPushButton(" Zip Converter")  # Removed extra space
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
                border-radius: 6px;
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
        self._settings_dialog = settings_dialog  # 保存对话框引用
        settings_dialog.show() # 使用show()而不是exec()，保持对话框非模态

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
    # 定义信号用于线程间通信
    update_status_signal = Signal(str, bool)
    
    def __init__(self, parent_window: IconButtonsWindow):
        super().__init__(parent_window)
        self.parent_window = parent_window # Store reference to the main window
        self.setWindowTitle("Settings")
                #self.setFixedSize(800, 600) # Increased size for better aesthetics and more content
        
        # 连接信号
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
            # 获取父窗口的主题设置，而不是根据系统palette判断
            theme_setting = self.parent_window.settings.value("theme", 0, type=int)
            if theme_setting == 0: # System Default
                # 只有当选择系统默认时才使用系统palette
                is_dark_mode = self.parent_window.palette().color(QPalette.ColorRole.Window).lightnessF() < 0.5
                self.apply_theme(is_dark_mode)
            elif theme_setting == 1: # Light Mode
                self.apply_theme(False)
            else: # Dark Mode
                self.apply_theme(True)
    def apply_theme(self, is_dark_mode):
        if is_dark_mode:
            self.setStyleSheet("""
                QDialog {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                    font-family: Arial, sans-serif;
                }
                QLabel {
                    color: #e0e0e0;
                }


                QPushButton {
                    background-color: #2196F3;
                    border: 1px solid #1976D2; /* Added border */
                    color: white;
                    padding: 8px 15px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 13px;
           
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
           
                }
                
                QComboBox {
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 6px 10px 6px 10px;
                    background-color: #2d2d2d;
                    color: #ffffff;
                    selection-background-color: #4a90e2;
                    selection-color: #ffffff;
                }
                QComboBox:editable {
                    background-color: #2d2d2d;
                }
                QComboBox:!editable, QComboBox::drop-down:editable {
                    background-color: #2d2d2d;
                }
                QComboBox:!editable:on, QComboBox::drop-down:editable:on {
                    background-color: #2d2d2d;
                }
                QComboBox:on {
                    background-color: #2d2d2d;
                }
                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 20px;
                    border-left-width: 1px;
                    border-left-color: #555555;
                    border-left-style: solid;
                    border-top-right-radius: 4px;
                    border-bottom-right-radius: 4px;
                    background-color: #2d2d2d;
                }
                QComboBox::down-arrow {
                    image: url(down_arrow_dark.svg);
                    width: 12px;
                    height: 12px;
                }
                QComboBox::down-arrow:on {
                    image: url(down_arrow_dark.svg);
                }
                QComboBox QAbstractItemView {
                    border: 1px solid #555555;
                    border-radius: 4px;
                    background-color: #2d2d2d;
                    color: #ffffff;
                    selection-background-color: #4a90e2;
                    selection-color: #ffffff;
                    outline: 0px;
                }
                QComboBox QAbstractItemView::item {
                    padding: 4px 10px;
                    border-radius: 2px;
                }
                QComboBox QAbstractItemView::item:selected {
                    background-color: #4a90e2;
                    color: #ffffff;
                }
                QComboBox QAbstractItemView::item:hover {
                    background-color: #3a3a3a;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: #f0f0f0;
                    color: #333;
                    font-family: Arial, sans-serif;
                }
                QLabel {
                    color: #333;
                }



                QPushButton {
                    background-color: #2196F3;
                    border: 1px solid #1976D2; /* Added border */
                    color: white;
                    padding: 8px 15px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 13px;
           
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
           
                }
                
                QComboBox {
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 6px 10px 6px 10px;
                    background-color: #ffffff;
                    color: #000000;
                    selection-background-color: #4a90e2;
                    selection-color: #ffffff;
                }
                QComboBox:editable {
                    background-color: #ffffff;
                }
                QComboBox:!editable, QComboBox::drop-down:editable {
                    background-color: #ffffff;
                }
                QComboBox:!editable:on, QComboBox::drop-down:editable:on {
                    background-color: #ffffff;
                }
                QComboBox:on {
                    background-color: #ffffff;
                }
                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 20px;
                    border-left-width: 1px;
                    border-left-color: #cccccc;
                    border-left-style: solid;
                    border-top-right-radius: 4px;
                    border-bottom-right-radius: 4px;
                    background-color: #ffffff;
                }
                QComboBox::down-arrow {
                    image: url(down_arrow.svg);
                    width: 12px;
                    height: 12px;
                }
                QComboBox::down-arrow:on {
                    image: url(down_arrow.svg);
                }
                QComboBox QAbstractItemView {
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    background-color: #ffffff;
                    color: #000000;
                    selection-background-color: #4a90e2;
                    selection-color: #ffffff;
                    outline: 0px;
                }
                QComboBox QAbstractItemView::item {
                    padding: 4px 10px;
                    border-radius: 2px;
                }
                QComboBox QAbstractItemView::item:selected {
                    background-color: #4a90e2;
                    color: #ffffff;
                }
                QComboBox QAbstractItemView::item:hover {
                    background-color: palette(alternate-base);
                }
                QPushButton {
                    background-color: #2196F3;
                    border: 1px solid #1976D2; /* Added border */
                    color: white;
                    padding: 8px 15px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 13px;
           
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
           
                }
                
                QGroupBox {
                    font-weight: bold;
                    margin-top: 10px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    background-color: #ffffff;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left; /* Position at top left */
                    padding: 0 5px;
                    color: #333; /* Title color */
                }
                #status_label {
                    color: #555;
                    font-size: 12px;
                    font-style: italic;
                }
                #settings_apply_button {
                    background-color: #4CAF50; /* Green for apply button */
                    border: 1px solid #388E3C; /* Added border */
           
                }
                #settings_apply_button:hover {
                    background-color: #43A047;
                }
                #settings_apply_button:pressed {
                    background-color: #2E7D32;
           
                }
                
                /* Update Button Styles */
                QPushButton#settings_button {
                    background-color: #2196F3; /* Blue */
                    border: none;
                    color: white;
                    padding: 12px 15px;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 14px;
                    text-align: center;
                }
                QPushButton#settings_button:hover {
                    background-color: #1976D2;
                }
                QPushButton#settings_button:pressed {
                    background-color: #0D47A1;
                }
            """)

    def init_ui(self):
        
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)



        update_group=UpdateDialog()
        update_group.setObjectName("update_group")
        main_layout.addWidget(update_group, 1, 0, 1, 2)
        # Spacer to push content to top
        main_layout.setRowStretch(2, 1)

        # 实时自动保存状态标签
        self.status_label = QLabel("Settings automatically saved")
        self.status_label.setObjectName("status_label")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.status_label.setVisible(False)
        
        status_layout = QHBoxLayout()
        status_layout.addStretch()
        status_layout.addWidget(self.status_label)
        main_layout.addLayout(status_layout, 3, 0, 1, 2)

    def load_settings(self):
        settings = QSettings("MyCompany", "ConverterApp")
        # Theme settings - always set to System Default (index 0)
        settings.setValue("theme", 0) # Force save System Default



    def _connect_settings_signals(self):
        """连接所有设置控件的信号到实时保存"""
        # 这里可以添加其他设置控件的信号连接
        # 例如：self.comboBox.currentIndexChanged.connect(self.save_settings_async)
        pass
    
    @Slot(str, bool)
    def _update_status_label(self, text, visible):
        """安全更新状态标签的槽函数"""
        self.status_label.setText(text)
        self.status_label.setVisible(visible)
    
    def save_settings_async(self):
        """在独立线程中异步保存设置"""
        def save_thread():
            settings = QSettings("MyCompany", "ConverterApp")
            # Theme settings - always System Default
            settings.setValue("theme", 0)
            settings.sync() # Ensure settings are written to disk
            
            # 通过信号在主线程中安全更新UI
            self.update_status_signal.emit("Settings saved", True)
            
            # 2秒后隐藏状态标签
            time.sleep(2)
            self.update_status_signal.emit("", False)
        
        # 启动独立线程执行保存操作
        thread = threading.Thread(target=save_thread)
        thread.daemon = True
        thread.start()
        
        # 立即应用主题变更
        if self.parent_window:
            self.parent_window._apply_system_theme_from_settings()
    
    def accept(self):
        """重写accept方法，只保存设置而不关闭对话框"""
        self.save_settings_async()
    
    def reject(self):
        """重写reject方法，保存设置并关闭对话框"""
        self.save_settings_async()
        super().reject()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    from support.toggle import theme_manager
    theme_manager.start()
    setTheme(Theme.AUTO)
    window = IconButtonsWindow(q_app=app)
    window.show()
    # Connect to palette changes for real-time theme switching ONLY if setting is System Default
    app.paletteChanged.connect(lambda: window._apply_system_theme(app.palette().color(QPalette.ColorRole.Window).lightnessF() < 0.5))
    exit_code = app.exec()
    theme_manager.stop()
    sys.exit(exit_code)