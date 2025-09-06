#!/usr/bin/env python3
"""
测试成功消息界面覆盖功能的脚本
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from gui_converter import ICNSConverterGUI


def test_success_overlay():
    """测试成功消息界面覆盖功能"""
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = ICNSConverterGUI()
    window.show()
    
    # 直接显示成功界面来测试覆盖效果
    window.show_success_view()
    
    print("测试窗口已显示，检查成功消息是否覆盖整个窗口")
    print("关闭窗口以结束测试")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    test_success_overlay()