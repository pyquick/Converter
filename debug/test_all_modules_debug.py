#!/usr/bin/env python3
"""
测试所有模块的debug增强输出功能
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))
# 添加debug文件夹到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_all_modules_debug():
    """测试所有模块的debug增强输出"""
    print("=== 测试所有模块的Debug增强输出 ===")
    
    # 启用debug模式
    from PySide6.QtCore import QSettings
    settings = QSettings("MyCompany", "ConverterApp")
    settings.setValue("debug_enabled", True)
    
    # 重新导入debug_logger以应用新设置
    import importlib
    from support import debug_logger
    importlib.reload(debug_logger)
    
    print("🔧 Debug模式已启用，开始测试各模块输出...")
    
    # 测试1: support模块
    try:
        from support import convert
        print("✅ support.convert模块导入成功")
        
        # 测试convert模块的输出
        print("测试convert模块输出...")
        
    except Exception as e:
        print(f"❌ support.convert模块导入失败: {e}")
    
    # 测试2: update模块
    try:
        from update import update_manager
        print("✅ update.update_manager模块导入成功")
        
        # 测试update模块的输出
        print("测试update模块输出...")
        
    except Exception as e:
        print(f"❌ update.update_manager模块导入失败: {e}")
    
    # 测试3: image_converter模块
    try:
        import image_converter
        print("✅ image_converter模块导入成功")
        
        # 测试image_converter模块的输出
        print("测试image_converter模块输出...")
        
    except Exception as e:
        print(f"❌ image_converter模块导入失败: {e}")
    
    # 测试4: arc_gui模块
    try:
        import arc_gui
        print("✅ arc_gui模块导入成功")
        
        # 测试arc_gui模块的输出
        print("测试arc_gui模块输出...")
        
    except Exception as e:
        print(f"❌ arc_gui模块导入失败: {e}")
    
    # 测试debug_logger函数
    try:
        from debug.debug_logger import debug_log, info_log
        debug_log("这是一条来自测试脚本的debug消息")
        info_log("这是一条来自测试脚本的info消息")
        print("✅ debug_logger函数调用成功")
        
    except Exception as e:
        print(f"❌ debug_logger函数调用失败: {e}")
    
    # 禁用debug模式
    settings.setValue("debug_enabled", False)
    print("🔧 Debug模式已禁用")
    
    # 测试普通输出
    print("测试普通输出(debug禁用)...")
    debug_log("这条消息应该正常显示")
    
    print("\n✅ 所有模块Debug增强输出测试完成！")

if __name__ == "__main__":
    test_all_modules_debug()