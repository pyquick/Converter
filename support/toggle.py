from termios import INPCK
from PySide6.QtWidgets import QWidget
import darkdetect
from qfluentwidgets import setTheme, setThemeColor, Theme
from qframelesswindow import QMainWindow
from qframelesswindow.utils import getSystemAccentColor
from darkdetect import isDark
from PySide6.QtCore import QThread, QTimer
import threading
import time
from con import CON
import weakref
import platform
from typing import Optional, Tuple
import gc

# 创建一个锁来保护对CON对象的访问
_con_lock = threading.Lock()
from qfluentwidgets import *

class ThemeManager(QObject):
    def __init__(self):
        super().__init__()
        setTheme(Theme.AUTO)
        # 定时器：每 1 秒检查一次
        
        setThemeColor(getSystemAccentColor(), save=False)
        self.current_theme = "dark"
        self.last_accent_color = None
        self.running = True
        self.system_theme_thread = None
        self.app_theme_thread = None
        self.accent_color_thread = None
        self.last_color_hex = None
        
    def check_accent_color(self):
        """检测系统主题色"""
        color = getSystemAccentColor()
        color_hex = color.name()

        if color_hex != self.last_color_hex:
            self.last_color_hex = color_hex
            color_dict = {
                "r": color.red(),
                "g": color.green(),
                "b": color.blue(),
                "a": color.alpha(),
                "hex": color_hex
            }
            self.on_color_change(color_dict)
    def on_color_change(self, color_dict):
        """当系统主题色变化时触发"""
        setThemeColor(getSystemAccentColor(), save=False)
        print("系统主题色变化:", color_dict)
    def start(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_accent_color)
        self.timer.start(100)
    def stop(self):
        pass
        
    


# 创建全局主题管理器实例
theme_manager = ThemeManager()
