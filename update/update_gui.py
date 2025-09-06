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
from .update_manager import UpdateManager
from .download_update import download_and_apply_update
from qframelesswindow.utils import getSystemAccentColor
from qfluentwidgets import *
import time

       
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
    progress_updated = Signal(int)
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
            def progress_callback(progress):
                if self._is_cancelled:
                    # 如果已取消，抛出异常停止下载
                    raise Exception("Download cancelled by user")
                self.progress_updated.emit(progress)
            
            result = download_and_apply_update(self.update_info, self.target_directory, progress_callback)
            self.download_finished.emit(result)
        except Exception as e:
            if "cancelled" in str(e).lower():
                self.download_finished.emit({"status": "cancelled", "message": "Download cancelled by user"})
            else:
                self.download_finished.emit({"status": "error", "message": str(e)})


class UpdateDialog(QWidget):
    __version__ = "2.0.0B3" 

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
        
        # 按钮容器
        button_container = QHBoxLayout()
        button_container.setSpacing(15)
        
        self.update_button = QPushButton("Check for Updates")
        self.update_button.setFixedSize(180, 60)
        self.update_button.clicked.connect(self.check_for_updates)
        
        self.download_button = QPushButton("Download Update")
        self.download_button.setFixedSize(180, 60)
        self.download_button.clicked.connect(self.download_update)
        self.download_button.setVisible(False)
        self.download_button.setEnabled(False)
        
        self.restart_button = QPushButton("Restart Application")
        self.restart_button.setFixedSize(180, 60)
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

    def check_for_updates(self):
        self.update_status_label.setText("Checking for updates...")
        self.update_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.start()
        QApplication.processEvents()  # 确保界面更新
        
        include_prerelease = self.include_prerelease_checkbox.isChecked()
        self.save_settings()
        
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
        elif result["status"] == "error":
            self.update_status_label.setText(f"❌ Check failed: {result['message']}")
            self.download_button.setVisible(False)
        else:
            self.update_status_label.setText(f"ℹ️ {result['message']}")
            self.download_button.setVisible(False)
        
        self.progress_bar.pause()
        self.progress_bar.setVisible(False)
        self.update_button.setEnabled(True)
    
    def download_update(self):
        if hasattr(self, 'current_update_info'):
            self.download_button.setEnabled(False)
            self.update_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.start()
            self.download_progress_bar.setVisible(False)
            self.update_status_label.setText("Download in progress...")
            
            # 添加数字进度标签
            if not hasattr(self, 'progress_label'):
                self.progress_label = QLabel("0%")
                self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                font = QFont()
                font.setPointSize(10)
                font.setBold(True)
                self.progress_label.setFont(font)
                # 找到进度条所在的布局并插入标签
                update_layout = self.findChild(QVBoxLayout)
                if update_layout:
                    # 在下载进度条后插入数字进度标签
                    progress_bar_index = update_layout.indexOf(self.download_progress_bar)
                    update_layout.insertWidget(progress_bar_index + 1, self.progress_label)
            else:
                self.progress_label.setText("0%")
                self.progress_label.setVisible(True)
            
            # 启动下载线程，下载到/Applications目录
            target_dir = "/Applications"
            os.makedirs(target_dir, exist_ok=True)
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
    
    def on_progress_updated(self, progress):
        # 更新进度条显示实际进度
        if progress > 0:
            # 显示实际进度条，隐藏不确定进度条
            self.progress_bar.setVisible(False)
            self.download_progress_bar.setVisible(True)
            self.download_progress_bar.setValue(progress)
            
            # 更新数字进度标签
            if hasattr(self, 'progress_label'):
                self.progress_label.setText(f"{progress}%")
        
        if progress == 100:
            self.progress_bar.pause()
        
    def on_download_finished(self, result):
        # 停止进度条
        if result["status"] == "success":
            self.progress_bar.pause()
        else:
            self.progress_bar.error()
        self.progress_bar.setVisible(False)
        self.download_progress_bar.setVisible(False)
        
        # 隐藏数字进度标签
        if hasattr(self, 'progress_label'):
            self.progress_label.setVisible(False)
        
        # 恢复下载按钮文本和功能
        self.download_button.setText("Download Update")
        self.download_button.clicked.disconnect()
        self.download_button.clicked.connect(self.download_update)
        
        if result["status"] == "success":
            self.update_status_label.setText(f"✅ {result['message']}\n\nPlease click 'Restart Application' to apply the update.")
            self.download_button.setVisible(False)
            self.restart_button.setVisible(True)
            self.restart_button.setEnabled(True)
            # 保存更新信息用于重启
            self.update_result = result
        elif result["status"] == "cancelled":
            self.update_status_label.setText("❌ Download cancelled by user")
            self.download_button.setEnabled(True)
            self.download_button.setVisible(True)
        else:
            self.update_status_label.setText(f"❌ Download failed: {result['message']}")
            self.download_button.setEnabled(True)
        
        self.update_button.setEnabled(True)
    
    def restart_application(self):
        """重启应用程序并应用更新"""
        if hasattr(self, 'update_result'):
            # 获取更新文件的路径
            temp_dir = self.update_result.get("temp_dir", "")
            if temp_dir and os.path.exists(temp_dir):
                # 执行更新脚本
                update_script_path = os.path.expanduser("~/.converter/update/com/update_apply.command")
                
                if os.path.exists(update_script_path):
                    try:
                        # 先执行更新脚本，传入系统临时目录路径
                        os.system(f"'{update_script_path}' '{temp_dir}' &")
                        print(f"✅ 更新脚本已执行: {update_script_path} with temp_dir: {temp_dir}")
                        
                        # 等待更新脚本执行完成后再进行清理
                        import time
                        time.sleep(3)  # 给更新脚本一些时间启动
                        
                        # 运行清理程序
                        downloader = self.update_result.get("downloader")
                        if downloader:
                            downloader.cleanup()
                            print(f"✅ 临时文件已清理: {temp_dir}")
                        
                        # 关闭当前应用程序
                        QApplication.quit()
                        
                    except Exception as e:
                        print(f"❌ 执行更新脚本时出错: {e}")
                        self.update_status_label.setText(f"❌ 重启失败: {e}")
                else:
                    print(f"❌ 更新脚本不存在: {update_script_path}")
                    self.update_status_label.setText("❌ 更新脚本不存在，请重新下载更新")
            else:
                print(f"❌ 更新文件路径无效: {temp_dir}")
                self.update_status_label.setText("❌ 更新文件路径无效，请重新下载更新")
        else:
            print("❌ update_result属性不存在")
            self.update_status_label.setText("❌ 更新信息丢失，请重新下载更新")

def main():
    app = QApplication(sys.argv)
    window = UpdateDialog()
    window.resize(500, 350)  # 扩大窗口大小以容纳更多内容
    window.show()
    sys.exit(app.exec())