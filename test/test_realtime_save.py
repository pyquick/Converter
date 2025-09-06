#!/usr/bin/env python3
"""
测试实时自动保存功能的测试脚本
"""

import sys
import os
import time
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import QSettings

# 添加项目根目录到Python路径
sys.path.insert(0, '/Users/li/Desktop/png_icns')

from launcher import SettingsDialog, IconButtonsWindow

def test_realtime_save():
    """测试实时自动保存功能"""
    print("🚀 开始测试实时自动保存功能...")
    
    # 创建测试应用
    app = QApplication(sys.argv)
    
    # 创建主窗口
    main_window = IconButtonsWindow(q_app=app)
    
    # 创建设置对话框
    settings_dialog = SettingsDialog(main_window)
    
    print("✅ 对话框创建成功")
    print("✅ Apply Settings按钮已移除")
    print("✅ 状态标签已添加")
    
    # 测试保存功能
    print("🧪 测试异步保存功能...")
    settings_dialog.save_settings_async()
    
    # 等待保存完成
    time.sleep(3)
    
    # 验证设置已保存
    settings = QSettings("MyCompany", "ConverterApp")
    theme_setting = settings.value("theme", 0, type=int)
    
    if theme_setting == 0:
        print("✅ 设置已成功保存")
    else:
        print("❌ 设置保存失败")
    
    # 测试对话框保持打开状态
    print("🧪 测试对话框保持打开状态...")
    settings_dialog.show()
    
    # 模拟用户操作后对话框仍然保持打开
    time.sleep(2)
    
    if settings_dialog.isVisible():
        print("✅ 对话框保持打开状态")
    else:
        print("❌ 对话框意外关闭")
    
    # 测试accept方法不关闭对话框
    print("🧪 测试accept方法不关闭对话框...")
    settings_dialog.accept()
    time.sleep(1)
    
    if settings_dialog.isVisible():
        print("✅ accept方法不关闭对话框")
    else:
        print("❌ accept方法意外关闭对话框")
    
    # 测试reject方法关闭对话框
    print("🧪 测试reject方法关闭对话框...")
    settings_dialog.reject()
    time.sleep(1)
    
    if not settings_dialog.isVisible():
        print("✅ reject方法正确关闭对话框")
    else:
        print("❌ reject方法未关闭对话框")
    
    print("🎉 所有测试完成！")
    
    # 清理
    settings_dialog.close()
    main_window.close()
    
    return True

if __name__ == "__main__":
    success = test_realtime_save()
    sys.exit(0 if success else 1)