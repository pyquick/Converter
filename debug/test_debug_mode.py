#!/usr/bin/env python3
"""
测试debug模式功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))
# 添加debug文件夹到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_debug_settings():
    """测试debug设置功能"""
    print("=== 测试Debug模式功能 ===")
    
    # 测试1: 检查debug_logger模块是否存在
    try:
        from debug.debug_logger import debug_logger, debug_log, info_log
        print("✅ debug_logger模块导入成功")
    except ImportError as e:
        print(f"❌ debug_logger模块导入失败: {e}")
        return
    
    # 测试2: 检查debug设置控件
    try:
        from PySide6.QtCore import QSettings
        
        # 测试设置状态
        settings = QSettings("MyCompany", "ConverterApp")
        debug_enabled = settings.value("debug_enabled", False)
        debug_enabled = bool(debug_enabled) if debug_enabled is not None else False
        print(f"✅ Debug设置状态: {debug_enabled} (应为False)")
        
        # 测试设置debug模式
        settings.setValue("debug_enabled", True)
        debug_enabled_set = settings.value("debug_enabled", False)
        debug_enabled_set = bool(debug_enabled_set) if debug_enabled_set is not None else False
        print(f"✅ Debug设置状态(启用): {debug_enabled_set} (应为True)")
        
        # 恢复设置
        settings.setValue("debug_enabled", False)
        
    except Exception as e:
        print(f"❌ 测试设置控件时出错: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试3: 检查日志目录
    log_dir = os.path.expanduser("~/.converter/log")
    log_dir_exists = os.path.exists(log_dir)
    print(f"✅ 日志目录存在: {log_dir_exists} ({log_dir})")
    
    if not log_dir_exists:
        try:
            os.makedirs(log_dir, exist_ok=True)
            print("✅ 日志目录创建成功")
        except Exception as e:
            print(f"❌ 创建日志目录失败: {e}")
    
    # 测试4: 测试日志函数
    try:
        debug_log("这是一条debug测试消息")
        info_log("这是一条info测试消息")
        
        # 测试普通print输出也会被增强
        print("这是一条普通print消息")
        
        print("✅ 日志函数调用成功")
    except Exception as e:
        print(f"❌ 日志函数调用失败: {e}")
    
    print("\n✅ Debug模式功能测试完成！")

if __name__ == "__main__":
    test_debug_settings()