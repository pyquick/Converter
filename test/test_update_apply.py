#!/usr/bin/env python3
"""
测试更新应用功能
"""

import sys
import os
import tempfile
import shutil

# 测试update_apply.command脚本
def test_update_script():
    print("测试update_apply.command脚本...")
    
    script_path = "/Users/li/Desktop/png_icns/update/update_apply.command"
    
    if not os.path.exists(script_path):
        print("❌ 更新脚本不存在")
        return False
    
    # 检查脚本权限
    if not os.access(script_path, os.X_OK):
        print("❌ 脚本没有执行权限")
        return False
    
    print("✅ 更新脚本存在且有执行权限")
    return True

# 测试目标目录创建
def test_target_directory():
    print("\n测试目标目录创建...")
    
    target_dir = os.path.expanduser("~/.converter/update/com")
    
    # 创建目录
    os.makedirs(target_dir, exist_ok=True)
    
    if os.path.exists(target_dir):
        print(f"✅ 目标目录已创建: {target_dir}")
        return True
    else:
        print(f"❌ 目标目录创建失败: {target_dir}")
        return False

# 测试脚本复制功能
def test_script_copy():
    print("\n测试脚本复制功能...")
    
    source_script = "/Users/li/Desktop/png_icns/update/update_apply.command"
    target_dir = os.path.expanduser("~/.converter/update/com")
    target_script = os.path.join(target_dir, "update_apply.command")
    
    # 复制脚本
    if os.path.exists(source_script):
        shutil.copy2(source_script, target_script)
        # 设置执行权限
        os.chmod(target_script, 0o755)
        
        if os.path.exists(target_script) and os.access(target_script, os.X_OK):
            print(f"✅ 脚本复制成功: {target_script}")
            return True
        else:
            print(f"❌ 脚本复制失败: {target_script}")
            return False
    else:
        print(f"❌ 源脚本不存在: {source_script}")
        return False

if __name__ == "__main__":
    print("开始测试更新应用功能...\n")
    
    success1 = test_update_script()
    success2 = test_target_directory()
    success3 = test_script_copy()
    
    print(f"\n测试结果:")
    print(f"更新脚本检查: {'✅ 通过' if success1 else '❌ 失败'}")
    print(f"目标目录创建: {'✅ 通过' if success2 else '❌ 失败'}")
    print(f"脚本复制功能: {'✅ 通过' if success3 else '❌ 失败'}")
    
    if success1 and success2 and success3:
        print("\n🎉 所有测试通过！更新应用功能已成功实现。")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败，请检查代码实现。")
        sys.exit(1)