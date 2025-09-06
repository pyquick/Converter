import darkdetect
from qfluentwidgets import setTheme, setThemeColor, Theme
from qframelesswindow.utils import getSystemAccentColor
from darkdetect import isDark
import threading
import time
from con import CON
import weakref
import platform
from typing import Optional, Tuple

# 创建一个锁来保护对CON对象的访问
_con_lock = threading.Lock()

class ThemeManager:
    def __init__(self):
        setTheme(Theme.AUTO)
        setThemeColor(getSystemAccentColor(), save=False)
        self.current_theme = "dark"
        self.last_accent_color = None
        self.running = True
        self.system_theme_thread = None
        self.app_theme_thread = None
        self.accent_color_thread = None
        
    def monitor_system_theme(self):
        """监控系统主题变化"""
        last_theme = None
        while self.running:
            try:
                is_dark = darkdetect.isDark()
                current_theme = "dark" if is_dark else "light"
                
                # 只在主题变化时更新
                if current_theme != last_theme:
                    # 使用锁保护对CON对象的访问
                    with _con_lock:
                        CON.theme_system = current_theme
                    last_theme = current_theme
                    print(f"System theme changed to: {current_theme}")
                
                time.sleep(0.3)  # 更快的检测频率
            except Exception as e:
                print(f"System theme monitoring error: {e}")
                break
    
    def monitor_app_theme(self):
        """监控应用主题变化并应用"""
        while self.running:
            try:
                # 使用锁保护对CON对象的访问
                with _con_lock:
                    theme_app = CON.theme_system
                
                # 检查是否需要更新主题
                if theme_app != self.current_theme:
                    if theme_app == "light":
                        setTheme(Theme.LIGHT)
                        self.current_theme = "light"
                        print(f"Application theme changed to: light")
                    elif theme_app == "dark":
                        setTheme(Theme.DARK)
                        self.current_theme = "dark"
                        print(f"Application theme changed to: dark")
                
                time.sleep(0.2)  # 更快的检测频率
                
            except Exception as e:
                print(f"App theme monitoring error: {e}")
                break
    
    def monitor_accent_color(self):
        """监控系统强调色变化"""
        while self.running:
            try:
                current_color = getSystemAccentColor()
                
                # 检查强调色是否变化
                if current_color != self.last_accent_color:
                    setThemeColor(current_color, save=False)
                    self.last_accent_color = current_color
                    print(f"Accent color changed to: {current_color.name()}")
                
                time.sleep(0.5)  # 强调色检测频率
                
            except Exception as e:
                print(f"Accent color monitoring error: {e}")
                break
    
    def start(self):
        """启动主题监控"""
        self.running = True
        
        # 初始化当前强调色
        self.last_accent_color = getSystemAccentColor()
        
        # 启动系统主题监控线程
        self.system_theme_thread = threading.Thread(
            target=self.monitor_system_theme, 
            daemon=True
        )
        self.system_theme_thread.start()
        
        # 启动应用主题监控线程
        self.app_theme_thread = threading.Thread(
            target=self.monitor_app_theme,
            daemon=True
        )
        self.app_theme_thread.start()
        
        # 启动强调色监控线程
        self.accent_color_thread = threading.Thread(
            target=self.monitor_accent_color,
            daemon=True
        )
        self.accent_color_thread.start()
    
    def stop(self):
        """停止主题监控"""
        self.running = False
        
        if self.system_theme_thread:
            self.system_theme_thread.join(timeout=1)
        
        if self.app_theme_thread:
            self.app_theme_thread.join(timeout=1)
            
        if self.accent_color_thread:
            self.accent_color_thread.join(timeout=1)

# 创建全局主题管理器实例
theme_manager = ThemeManager()
