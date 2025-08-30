import sys
import os
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpacerItem,
    QSizePolicy
)
from PySide6.QtGui import QIcon, QPainter, QPixmap, QPalette
from PySide6.QtCore import QSize, Qt
import subprocess # Import subprocess
import multiprocessing # Keep for freeze_support, but remove direct Process usage


# --- 用于创建占位符图标的辅助函数 ---
# 因为无法直接生成 .icns 文件，我们创建 PNG 文件作为示例。
# 请将 AppIcon.icns 和 zip.icns 文件放置在与此脚本相同的目录中。
def create_placeholder_icon(path: str, color: str, text: str):
    """如果图标文件不存在，则创建一个简单的 PNG 占位符图标。"""
    if not os.path.exists(path):
        pixmap = QPixmap(128, 128)
        pixmap.fill(color)
        painter = QPainter(pixmap)
        painter.setPen("white")
        font = painter.font()
        font.setPointSize(48)
        painter.setFont(font)
        # Qt.AlignCenter 是枚举值 1
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
        painter.end()
        pixmap.save(path)
        print(f"提示：未找到 '{path}'。已创建一个占位符图标。")
        return True
    # 如果是 .icns 文件，则直接使用
    elif path.endswith(".icns") and os.path.exists(path):
        return True
    # 如果存在非 .icns 的占位符文件，也视为成功
    elif not path.endswith(".icns") and os.path.exists(path):
        return True
    return False

class IconButtonsWindow(QWidget):
    
    LIGHT_QSS = """
        QWidget {
            background-color: #f0f0f0;
            font-family: Arial, sans-serif;
            color: #333;
        }
        QLabel {
            color: #333;
        }
        QPushButton {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            font-size: 16px;
            margin: 4px 2px;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        #title_label {
            color: #333;
        }
        #button_app {
            background-color: #2196F3;
        }
        #button_app:hover {
            background-color: #1976D2;
        }
        #button_app:pressed {
            background-color: #0D47A1;
        }
        #button_zip {
            background-color: #9E9E9E;
        }
        #button_zip:hover {
            background-color: #757575;
        }
        #button_zip:pressed {
            background-color: #424242;
        }
    """

    DARK_QSS = """
        QWidget {
            background-color: #2b2b2b;
            font-family: Arial, sans-serif;
            color: #e0e0e0;
        }
        QLabel {
            color: #e0e0e0;
        }
        QPushButton {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            font-size: 16px;
            margin: 4px 2px;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        #title_label {
            color: #e0e0e0;
        }
        #button_app {
            background-color: #2196F3;
        }
        #button_app:hover {
            background-color: #1976D2;
        }
        #button_app:pressed {
            background-color: #0D47A1;
        }
        #button_zip {
            background-color: #9E9E9E;
        }
        #button_zip:hover {
            background-color: #757575;
        }
        #button_zip:pressed {
            background-color: #424242;
        }
    """

    def __init__(self, initial_dark_mode=False):
        super().__init__()
        self.setWindowTitle("Converter")
        self.setGeometry(200, 200, 400, 300)
        self.path= os.path.dirname(os.path.abspath(__file__))
        # 定义图标文件的路径
        self.app_icon_path = os.path.join(self.path,"AppIcon.png")
        self.appd_icon_path = os.path.join(self.path,"AppIcond.png")
        self.zip_icon_path = os.path.join(self.path,"zip.png")
        self.zipd_icon_path = os.path.join(self.path,"zipd.png")

        # 检查图标文件是否存在，并创建占位符（如果需要）
        # 对于 AppIcon
        if not os.path.exists(self.app_icon_path):
            print("提示：AppIcon.png 文件未找到。将尝试创建 PNG 占位符图标。")
            # Note: The original request for AppIcon placeholder path was './AppIcon.icns'
            # which means it would create a PNG with .icns extension. This is inconsistent.
            # For consistency with zip.png placeholder, changing to .png for placeholder.
            # If the user provides a proper .icns file, it will be used.
            self.app_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AppIcon.png")
            create_placeholder_icon(self.app_icon_path, "dodgerblue", "App")
        if not os.path.exists(self.appd_icon_path):
            print("提示：AppIcond.png 文件未找到。将尝试创建 PNG 占位符图标。")
            # Note: The original request for AppIcon placeholder path was './AppIcon.icns'
            # which means it would create a PNG with .icns extension. This is inconsistent.
            # For consistency with zip.png placeholder, changing to .png for placeholder.
            # If the user provides a proper .icns file, it will be used.
            self.app_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AppIcond.png")
            create_placeholder_icon(self.appd_icon_path, "dodgerblue", "AppD")
        
        # 对于 zip.png
        if not os.path.exists(self.zip_icon_path):
            print("提示：zip.png 文件未找到。将尝试创建 PNG 占位符图标。")
            # Again, adjusting path to ensure .png placeholder if original is missing.
            self.zip_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zip.png")
            create_placeholder_icon(self.zip_icon_path, "gray", "Zip")

        # 对于 zipd.png
        if not os.path.exists(self.zipd_icon_path):
            print("提示：zipd.png 文件未找到。将尝试创建 PNG 占位符图标。")
            # Use a slightly different color for dark mode placeholder to distinguish
            self.zipd_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zipd.png")
            create_placeholder_icon(self.zipd_icon_path, "dimgray", "ZipD")

        self.init_ui()
        self._apply_theme(initial_dark_mode) # Apply theme after UI is initialized
    
    def _apply_system_theme(self, is_dark_mode):
        self._apply_theme(is_dark_mode)

    def _apply_theme(self, is_dark_mode):
        if is_dark_mode:
            self.setStyleSheet(self.DARK_QSS)
            # Set zip icon for dark mode
            if hasattr(self, 'button_zip'):
                self.button_zip.setIcon(QIcon(self.zipd_icon_path))
            if hasattr(self, 'button_app'):
                self.button_app.setIcon(QIcon(self.appd_icon_path))
        else:
            self.setStyleSheet(self.LIGHT_QSS)
            # Set zip icon for light mode
            if hasattr(self, 'button_zip'):
                self.button_zip.setIcon(QIcon(self.zip_icon_path))
            if hasattr(self, 'button_app'):
                self.button_app.setIcon(QIcon(self.app_icon_path))

    def init_ui(self):
        
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # 添加标题
        title_label = QLabel("Converter")
        title_label.setObjectName("title_label") # Add object name for QSS
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        """) # Remove color from here, control via QSS
        main_layout.addWidget(title_label)

        # --- 按钮 1: AppIcon ---
        # 创建 QIcon 对象
        # The icon is set based on the theme in _apply_theme, so just initialize with a default
        app_icon = QIcon(self.app_icon_path)

        # 创建按钮并设置图标
        self.button_app = QPushButton("Image Converter")
        self.button_app.setObjectName("button_app") # Add object name for QSS
        self.button_app.setIcon(app_icon)
        self.button_app.setIconSize(QSize(64, 64))
        self.button_app.setMinimumHeight(80)
        self.button_app.clicked.connect(run_image_app) # Connect to a method within the class
        # Remove style from here, control via QSS

        # --- 按钮 2: zip.icns ---
        # 创建 QIcon 对象
        # The icon is set based on the theme in _apply_theme, so just initialize with a default
        zip_icon = QIcon(self.zip_icon_path)

        # 创建按钮并设置图标
        self.button_zip = QPushButton("Zip Converter")
        self.button_zip.setObjectName("button_zip") # Add object name for QSS
        self.button_zip.setIcon(zip_icon)
        self.button_zip.setIconSize(QSize(64,64))
        self.button_zip.setMinimumHeight(85)
        self.button_zip.clicked.connect(run_zip_app) # Connect to a method within the class
        # Remove style from here, control via QSS

        # 创建水平布局来居中按钮
        app_button_layout = QHBoxLayout()
        app_button_layout.addStretch()
        app_button_layout.addWidget(self.button_app)
        app_button_layout.addStretch()
        
        zip_button_layout = QHBoxLayout()
        zip_button_layout.addStretch()
        zip_button_layout.addWidget(self.button_zip)
        zip_button_layout.addStretch()

        # 将按钮添加到布局中
        main_layout.addLayout(app_button_layout)
        main_layout.addLayout(zip_button_layout)
        
        # 添加垂直空间
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # 设置窗口的主布局
        self.setLayout(main_layout)
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

if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    
    # Detect initial theme
    palette = app.palette()
    is_dark_mode = palette.color(QPalette.ColorRole.Window).lightnessF() < 0.5
    
    window = IconButtonsWindow(initial_dark_mode=is_dark_mode)
    window.show()
    # Connect to palette changes for real-time theme switching
    app.paletteChanged.connect(lambda: window._apply_system_theme(app.palette().color(QPalette.ColorRole.Window).lightnessF() < 0.5))
    sys.exit(app.exec())