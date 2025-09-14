# -*- coding: utf-8 -*-
#Please do not change import
from concurrent.futures import thread
import multiprocessing
import sys
import os
import threading

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QGroupBox,
    QSpacerItem,
    QSizePolicy,
    QProgressBar,
    QAbstractButton
)
from PySide6.QtCore import QSettings, Qt, QThread, Signal
from PySide6.QtGui import QFont
from darkdetect import isDark
from update.update_manager import UpdateManager
from update.download_update import download_and_apply_update
from qframelesswindow.utils import getSystemAccentColor
from qfluentwidgets import *
import time
from con import CON
class CheckUpdateThread(QThread):
    check_finished = Signal(dict)
    
    def __init__(self, update_manager, include_prerelease):
        super().__init__()
        self.update_manager = update_manager
        self.include_prerelease = include_prerelease
    
    def run(self):
        try:
            result = self.update_manager.check_for_updates(self.include_prerelease)
            self.check_finished.emit(result)
        except Exception as e:
            self.check_finished.emit({"status": "error", "message": str(e)})


class DownloadThread(QThread):
    progress_updated = Signal(int, int, int)  # 进度百分比, 已下载字节, 总字节
    download_finished = Signal(dict)
    
    def __init__(self, update_info, target_directory):
        super().__init__()
        self.update_info = update_info
        self.target_directory = target_directory
        self._is_cancelled = False
        
    def cancel(self):
        """取消下载"""
        self._is_cancelled = True
    
    def run(self):
        try:
            # 定义进度回调函数
            def progress_callback(progress, downloaded_bytes, total_bytes):
                if self._is_cancelled:
                    # 如果已取消，抛出异常停止下载
                    raise Exception("Download cancelled by user")
                self.progress_updated.emit(progress, downloaded_bytes, total_bytes)
            
            result = download_and_apply_update(self.update_info, self.target_directory, progress_callback)
            self.download_finished.emit(result)
        except Exception as e:
            if "cancelled" in str(e).lower():
                self.download_finished.emit({"status": "cancelled", "message": "Download cancelled by user"})
            else:
                self.download_finished.emit({"status": "error", "message": str(e)})


class UpdateDialog(QWidget):
    __version__ = "2.0.0B4" 

    def __init__(self):
        super().__init__()
        # 移除SystemThemeListener以避免线程问题
        # self.themeListener = SystemThemeListener(self)
       
        
        self.setWindowTitle("Update Settings")
        self.update_manager = UpdateManager(self.__version__)
        self.check_thread = None
        self.download_thread = None
       
        
        self.init_ui()
        self.load_settings()
        self.connect_auto_save_signals()
       
    def closeEvent(self, e):
       
        super().closeEvent(e)
    

    def init_ui(self):
       
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        update_group = QGroupBox("Update Settings")
        update_layout = QVBoxLayout()
        update_layout.setContentsMargins(25, 25, 25, 25)
        update_layout.setSpacing(20)
        
        # 添加顶部间距
        update_layout.addSpacerItem(QSpacerItem(0, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        
        # 创建开关样式的checkbox
        self.include_prerelease_checkbox = CheckBox("Include pre-releases in update checks")
        self.include_prerelease_checkbox.setMinimumHeight(60)
        update_layout.addWidget(self.include_prerelease_checkbox)
        
        self.update_status_label = QLabel("Ready to check for updates.")
        self.update_status_label.setMinimumHeight(60)
        self.update_status_label.setMinimumWidth(550)
        self.update_status_label.setWordWrap(True)
        #self.update_status_label.setStyleSheet("QLabel { padding: 8px; background-color: #f8f9fa; border-radius: 5px; }")
        update_layout.addWidget(self.update_status_label)
        
        # 更新内容显示区域
        self.release_content_browser = TextBrowser()
        self.release_content_browser.setMinimumHeight(150)
        self.release_content_browser.setVisible(False)
        update_layout.addWidget(self.release_content_browser)
        
        # 下载进度条
        self.progress_bar = IndeterminateProgressBar()
        self.progress_bar.setVisible(False)
        update_layout.addWidget(self.progress_bar)
        
        # 实际下载进度条
        self.download_progress_bar = ProgressBar()
        self.download_progress_bar.setRange(0, 100)
        self.download_progress_bar.setValue(0)
        self.download_progress_bar.setVisible(False)
        update_layout.addWidget(self.download_progress_bar)
        
        # 进度标签（显示百分比、下载大小、速度等信息）
        self.progress_label = QLabel("0%")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.progress_label.setFont(font)
        self.progress_label.setVisible(False)
        update_layout.addWidget(self.progress_label)
        
        # 按钮容器
        button_container = QHBoxLayout()
        button_container.setSpacing(15)
        
        self.update_button = PrimaryPushButton("Check for Updates")
        self.update_button.setFixedSize(180, 60)
        setCustomStyleSheet(self.update_button, CON.qss_debug, CON.qss_debug)
        self.update_button.clicked.connect(self.check_for_updates)
        
        self.download_button =PrimaryPushButton("Download Update")
        self.download_button.setFixedSize(180, 60)
        setCustomStyleSheet(self.download_button, CON.qss_debug, CON.qss_debug)
        self.download_button.clicked.connect(self.download_update)
        self.download_button.setVisible(False)
        self.download_button.setEnabled(False)
        
        self.restart_button = PrimaryPushButton("Restart Application")
        self.restart_button.setFixedSize(180, 60)
        setCustomStyleSheet(self.restart_button, CON.qss_debug, CON.qss_debug)
        self.restart_button.clicked.connect(self.restart_application)
        self.restart_button.setVisible(False)
        self.restart_button.setEnabled(False)
        
        button_container.addStretch()
        button_container.addWidget(self.update_button)
        button_container.addWidget(self.download_button)
        button_container.addWidget(self.restart_button)
        button_container.addStretch()
        update_layout.addLayout(button_container)
        
        # 添加底部间距
        update_layout.addSpacerItem(QSpacerItem(0, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        
        update_group.setLayout(update_layout)
        main_layout.addWidget(update_group)
        
        self.setLayout(main_layout)

    
        
        # 设置按钮字体
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.update_button.setFont(font)
        self.download_button.setFont(font)
        self.restart_button.setFont(font)
        
        # 设置标签字体
        label_font = QFont()
        label_font.setPointSize(11)
        self.update_status_label.setFont(label_font)
        
        # 设置复选框字体
        checkbox_font = QFont()
        checkbox_font.setPointSize(11)
        self.include_prerelease_checkbox.setFont(checkbox_font)
       
       
       
         

    def load_settings(self):
        settings = QSettings("MyCompany", "ConverterApp")
        include_prerelease = str(settings.value("include_prerelease", False)).lower() == "true"
        self.include_prerelease_checkbox.setChecked(include_prerelease)

    def save_settings(self):
        settings = QSettings("MyCompany", "ConverterApp")
        settings.setValue("include_prerelease", self.include_prerelease_checkbox.isChecked())
        settings.sync()
    
    def connect_auto_save_signals(self):
        """Connect UI controls to auto-save functionality"""
        # Connect checkbox to auto-save
        self.include_prerelease_checkbox.stateChanged.connect(self.auto_save_settings)
    
    def auto_save_settings(self):
        """Auto-save settings immediately upon change"""
        try:
            # Save settings immediately
            self.save_settings()
            
            # Try to notify parent settings dialog about the save
            parent_widget = self.parent()
            while parent_widget:
                if hasattr(parent_widget, 'update_status_signal') and hasattr(parent_widget.update_status_signal, 'emit'):
                    # Found settings dialog, emit save notification
                    #parent_widget.update_status_signal.emit("Settings saved", True)
                    break
                parent_widget = parent_widget.parent()
                
        except Exception as e:
            print(f"Error in auto_save_settings: {e}")

    def check_for_updates(self):
        self.update_status_label.setText("Checking for updates...")
        setThemeColor(getSystemAccentColor(), save=False)
        self.update_button.setEnabled(False)
        
        # 隐藏TextBrowser、下载按钮和重启按钮
        self.release_content_browser.setVisible(False)
        self.download_button.setVisible(False)
        self.restart_button.setVisible(False)
        
        # 显示进度条并设置主题色
        self.progress_bar.setVisible(True)
        self.progress_bar.resume()
        self.progress_bar.start()
        QApplication.processEvents()  # 确保界面更新
        
        include_prerelease = self.include_prerelease_checkbox.isChecked()
        # Auto-save settings immediately when checking for updates
        self.auto_save_settings()
        
        # 启动检查更新线程
        self.check_thread = CheckUpdateThread(self.update_manager, include_prerelease)
        self.check_thread.check_finished.connect(self.on_check_finished)
        self.check_thread.start()
    
    def on_check_finished(self, result):
        if result["status"] == "update_available":
            self.update_status_label.setText(f"✅ {result['message']}\n\nVersion: {result['latest_version']}")
            self.download_button.setVisible(True)
            self.download_button.setEnabled(True)
            self.current_update_info = result
            
            # 显示更新内容
            if result.get("release_body"):
                self.release_content_browser.setMarkdown(result["release_body"])
                self.release_content_browser.setVisible(True)
            else:
                self.release_content_browser.setVisible(False)
        elif result["status"] == "error":
            self.update_status_label.setText(f"❌ Check failed: {result['message']}")
            self.download_button.setVisible(False)
            self.release_content_browser.setVisible(False)
        else:
            self.update_status_label.setText(f"ℹ️ {result['message']}")
            self.download_button.setVisible(False)
            self.release_content_browser.setVisible(False)
        
        self.progress_bar.pause()
        self.progress_bar.setVisible(False)
        self.update_button.setEnabled(True)
    
    def download_update(self):
        if hasattr(self, 'current_update_info'):
            self.download_button.setEnabled(False)
            self.update_button.setEnabled(False)
            
            # 隐藏TextBrowser
            self.release_content_browser.setVisible(False)
            
            self.progress_bar.setVisible(True)
            self.progress_bar.start()
            self.download_progress_bar.setVisible(False)
            self.update_status_label.setText("Download in progress...")
            
            # 显示进度标签
            self.progress_label.setText("0%")
            self.progress_label.setVisible(True)
            
            # 启动下载线程，下载到/Applications目录
            target_dir = "/Applications"
            os.makedirs(target_dir, exist_ok=True)
            
            # 重置下载计时器
            if hasattr(self, '_download_start_time'):
                delattr(self, '_download_start_time')
            if hasattr(self, '_last_downloaded'):
                delattr(self, '_last_downloaded')
            if hasattr(self, '_last_time'):
                delattr(self, '_last_time')
            
            self.download_thread = DownloadThread(self.current_update_info, target_dir)
            self.download_thread.progress_updated.connect(self.on_progress_updated)
            self.download_thread.download_finished.connect(self.on_download_finished)
            self.download_thread.start()
            
            # 将下载按钮改为取消按钮
            self.download_button.setText("Cancel Download")
            self.download_button.setEnabled(True)
            self.download_button.clicked.disconnect()
            self.download_button.clicked.connect(self.cancel_download)
    
    def cancel_download(self):
        """取消下载"""
        if hasattr(self, 'download_thread') and self.download_thread is not None and self.download_thread.isRunning():
            self.download_thread.cancel()
            self.download_button.setEnabled(False)
            self.update_status_label.setText("Cancelling download...")
    
    def start_swing_animation(self):
        """启动左右摆动动画"""
        pass
    
    def update_swing_animation(self):
        """更新摆动动画"""
        pass
    
    def on_progress_updated(self, progress, downloaded_bytes, total_bytes):
        # 更新进度条显示实际进度
        if progress > 0:
            # 显示实际进度条，隐藏不确定进度条
            self.progress_bar.setVisible(False)
            self.download_progress_bar.setVisible(True)
            self.download_progress_bar.setValue(progress)
            
            # 计算下载速度和时间估计
            current_time = time.time()
            if not hasattr(self, '_download_start_time'):
                self._download_start_time = current_time
                self._last_downloaded = 0
                self._last_time = current_time
            
            # 计算瞬时速度
            time_diff = current_time - self._last_time
            if time_diff > 0.5:  # 每0.5秒更新一次速度
                downloaded_diff = downloaded_bytes - self._last_downloaded
                download_speed = downloaded_diff / time_diff  # bytes per second
                
                # 计算剩余时间
                remaining_bytes = total_bytes - downloaded_bytes
                if download_speed > 0:
                    remaining_time = remaining_bytes / download_speed
                    # 格式化剩余时间
                    if remaining_time > 3600:
                        eta_str = f"{remaining_time/3600:.1f}h"
                    elif remaining_time > 60:
                        eta_str = f"{remaining_time/60:.1f}m"
                    else:
                        eta_str = f"{remaining_time:.1f}s"
                else:
                    eta_str = "未知"
                
                # 格式化文件大小
                def format_size(bytes_size):
                    if bytes_size >= 1024*1024*1024:
                        return f"{bytes_size/(1024*1024*1024):.2f} GB"
                    elif bytes_size >= 1024*1024:
                        return f"{bytes_size/(1024*1024):.2f} MB"
                    elif bytes_size >= 1024:
                        return f"{bytes_size/1024:.2f} KB"
                    else:
                        return f"{bytes_size} B"
                
                # 更新数字进度标签
                if hasattr(self, 'progress_label'):
                    downloaded_str = format_size(downloaded_bytes)
                    total_str = format_size(total_bytes)
                    speed_str = format_size(download_speed) + "/s"
                    
                    self.progress_label.setText(
                        f"{progress}% - {downloaded_str}/{total_str} - {speed_str} - 剩余: {eta_str}"
                    )
                
                self._last_downloaded = downloaded_bytes
                self._last_time = current_time
        
        if progress == 100:
            self.progress_bar.pause()
        
    def on_download_finished(self, result):
        # 停止进度条
        if result["status"] == "success":
            # 下载成功，立即开始应用更新
            self.progress_bar.pause()
            self.progress_bar.setVisible(False)
            self.download_progress_bar.setVisible(False)
            
            # 隐藏数字进度标签
            if hasattr(self, 'progress_label'):
                self.progress_label.setVisible(False)
            
            # 清理下载计时器变量
            if hasattr(self, '_download_start_time'):
                delattr(self, '_download_start_time')
            if hasattr(self, '_last_downloaded'):
                delattr(self, '_last_downloaded')
            if hasattr(self, '_last_time'):
                delattr(self, '_last_time')
            
            # 保存更新信息
            self.update_result = result
            
            # 显示应用更新进度
            self.update_status_label.setText("Applying updates...")
            
            # 使用IndeterminateProgressBar显示应用更新进度
            self.progress_bar.setVisible(True)
            self.progress_bar.start()
            
            # 立即执行更新应用
            self.apply_update()
            
        else:
            # 下载失败或取消
            if result["status"] == "cancelled":
                
                self.update_status_label.setText("❌ Download cancelled by user")
            else:
                # 确保错误消息正确处理非ASCII字符
                try:
                    error_message = str(result['message'])
                    self.update_status_label.setText(f"❌ 下载失败: {error_message}")
                except Exception as e:
                    # 如果出现编码问题，显示基本错误信息
                    self.update_status_label.setText(f"❌ 下载失败: 处理错误消息时出现编码问题")
            
            self.progress_bar.setVisible(False)
            self.download_progress_bar.setVisible(False)
            
            # 隐藏数字进度标签
            if hasattr(self, 'progress_label'):
                self.progress_label.setVisible(False)
            
            # 清理下载计时器变量
            if hasattr(self, '_download_start_time'):
                delattr(self, '_download_start_time')
            if hasattr(self, '_last_downloaded'):
                delattr(self, '_last_downloaded')
            if hasattr(self, '_last_time'):
                delattr(self, '_last_time')
            
            # 恢复下载按钮
            self.download_button.setText("Download Update")
            self.download_button.clicked.disconnect()
            self.download_button.clicked.connect(self.download_update)
            self.download_button.setEnabled(True)
            self.download_button.setVisible(True)
            
            self.update_button.setEnabled(True)
    
    def apply_update(self):
        """应用更新"""
        if hasattr(self, 'update_result'):
            # 获取更新文件的路径
            temp_dir = self.update_result.get("temp_dir", "")
            if temp_dir and os.path.exists(temp_dir):
                # 执行更新脚本
                update_script_path = os.path.join(os.path.dirname(__file__), "update_apply.command")
                
                if os.path.exists(update_script_path):
                    try:
                        # 执行更新脚本
                        os.system(f"'{update_script_path}' '{temp_dir}' &")
                        print(f"✅ 更新脚本已执行: {update_script_path} with temp_dir: {temp_dir}")
                        
                        # 更新状态显示
                        self.update_status_label.setText("✅ Update applied successfully! Please restart the application.")
                        
                        # 显示重启按钮
                        self.restart_button.setVisible(True)
                        self.restart_button.setEnabled(True)
                        
                        # 停止进度条
                        self.progress_bar.pause()
                        self.progress_bar.setVisible(False)
                        
                    except Exception as e:
                        print(f"❌ 执行更新脚本时出错: {e}")
                        self.update_status_label.setText(f"❌ Apply update failed: {e}")
                        
                else:
                    print(f"❌ 更新脚本不存在: {update_script_path}")
                    self.update_status_label.setText("❌ Update script not found, please restart manually")
                    
            else:
                print(f"❌ 更新文件路径无效: {temp_dir}")
                self.update_status_label.setText("❌ Update files not found, please restart manually")
                
        else:
            print("❌ update_result属性不存在")
            self.update_status_label.setText("❌ Update information lost, please restart manually")
            

     
    def restart_application(self):
        """重启应用程序"""
        try:
            # 执行重启脚本
            restart_script_path = os.path.join(os.path.dirname(__file__), "restart.command")
            
            if os.path.exists(restart_script_path):
                # 执行重启脚本
                os.system(f"'{restart_script_path}' &")
                print(f"✅ 重启脚本已执行: {restart_script_path}")
                
                # 关闭当前应用程序
                QApplication.quit()
                
            else:
                print(f"❌ 重启脚本不存在: {restart_script_path}")
                self.update_status_label.setText("❌ Restart script not found, please restart manually")
                
        except Exception as e:
            print(f"❌ 执行重启脚本时出错: {e}")
            self.update_status_label.setText(f"❌ Restart failed: {e}")

def main():
    app = QApplication(sys.argv)
    window = UpdateDialog()
    window.resize(500, 350)  # 扩大窗口大小以容纳更多内容
    window.show()
    sys.exit(app.exec())