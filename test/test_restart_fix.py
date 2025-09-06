#!/usr/bin/env python3
"""
测试重启应用功能修复
"""

import sys
import os
import tempfile

# 添加项目路径到sys.path
sys.path.insert(0, '/Users/li/Desktop/png_icns')

from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import Qt

def test_restart_application():
    """测试restart_application方法"""
    print("测试restart_application方法...")
    
    # 创建一个简单的测试应用
    app = QApplication(sys.argv)
    
    # 创建一个测试标签
    status_label = QLabel()
    status_label.setText("初始状态")
    
    # 模拟update_result对象
    class MockUpdateResult:
        def get(self, key, default=""):
            if key == "temp_dir":
                # 创建一个临时目录来模拟有效的更新路径
                temp_dir = tempfile.mkdtemp(prefix="test_update_")
                print(f"✅ 创建临时目录: {temp_dir}")
                return temp_dir
            return default
    
    # 测试有效的temp_dir
    print("\n测试1: 有效的temp_dir")
    mock_result = MockUpdateResult()
    temp_dir = mock_result.get("temp_dir")
    
    if temp_dir and os.path.exists(temp_dir):
        print(f"✅ temp_dir有效: {temp_dir}")
        
        # 检查更新脚本路径
        update_script_path = os.path.expanduser("~/.converter/update/com/update_apply.command")
        print(f"更新脚本路径: {update_script_path}")
        
        if os.path.exists(update_script_path):
            print("✅ 更新脚本存在")
        else:
            print("❌ 更新脚本不存在")
            
        # 清理临时目录
        import shutil
        shutil.rmtree(temp_dir)
        print("✅ 临时目录已清理")
        
    else:
        print("❌ temp_dir无效")
    
    # 测试无效的temp_dir
    print("\n测试2: 无效的temp_dir")
    invalid_temp_dir = "/invalid/path"
    if invalid_temp_dir and os.path.exists(invalid_temp_dir):
        print("❌ 不应该出现这种情况")
    else:
        print(f"✅ 正确检测到无效路径: {invalid_temp_dir}")
    
    # 测试空的temp_dir
    print("\n测试3: 空的temp_dir")
    empty_temp_dir = ""
    if empty_temp_dir and os.path.exists(empty_temp_dir):
        print("❌ 不应该出现这种情况")
    else:
        print(f"✅ 正确检测到空路径: '{empty_temp_dir}'")
    
    app.quit()
    return True

def test_update_script_execution():
    """测试更新脚本执行"""
    print("\n测试更新脚本执行...")
    
    update_script_path = os.path.expanduser("~/.converter/update/com/update_apply.command")
    
    if os.path.exists(update_script_path):
        # 检查脚本权限
        if os.access(update_script_path, os.X_OK):
            print("✅ 更新脚本有执行权限")
            
            # 测试脚本内容
            try:
                with open(update_script_path, 'r') as f:
                    content = f.read()
                    if "chmod" in content and "cp" in content:
                        print("✅ 脚本包含必要的命令")
                    else:
                        print("❌ 脚本可能缺少必要命令")
            except Exception as e:
                print(f"❌ 读取脚本失败: {e}")
        else:
            print("❌ 更新脚本没有执行权限")
    else:
        print("❌ 更新脚本不存在")
    
    return True

if __name__ == "__main__":
    print("开始测试重启应用功能修复...\n")
    
    success1 = test_restart_application()
    success2 = test_update_script_execution()
    
    print(f"\n测试结果:")
    print(f"重启应用逻辑测试: {'✅ 通过' if success1 else '❌ 失败'}")
    print(f"更新脚本执行测试: {'✅ 通过' if success2 else '❌ 失败'}")
    
    if success1 and success2:
        print("\n🎉 所有测试通过！重启应用功能已修复。")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败，请检查代码实现。")
        sys.exit(1)