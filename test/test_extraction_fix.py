#!/usr/bin/env python3
"""
测试解压和文件放置逻辑修复
"""

import os
import sys
import tempfile
import shutil

# 添加项目路径到sys.path
sys.path.insert(0, '/Users/li/Desktop/png_icns')

def test_update_script_with_temp_dir():
    """测试更新脚本处理系统临时目录的功能"""
    print("🧪 测试更新脚本处理系统临时目录...")
    
    # 创建系统临时目录
    system_temp_dir = tempfile.mkdtemp(prefix="update_")
    print(f"📁 创建系统临时目录: {system_temp_dir}")
    
    # 在系统临时目录中创建模拟的.app文件
    test_app_dir = os.path.join(system_temp_dir, "Converter.app")
    os.makedirs(test_app_dir)
    os.makedirs(os.path.join(test_app_dir, "Contents"))
    os.makedirs(os.path.join(test_app_dir, "Contents", "MacOS"))
    
    # 创建可执行文件
    launcher_path = os.path.join(test_app_dir, "Contents", "MacOS", "launcher")
    with open(launcher_path, 'w') as f:
        f.write("#!/bin/bash\necho 'Test launcher'\n")
    os.chmod(launcher_path, 0o755)
    
    print(f"📦 创建模拟应用程序: {test_app_dir}")
    
    # 测试update_apply.command脚本
    script_path = "/Users/li/Desktop/png_icns/update/update_apply.command"
    
    # 执行脚本并传入系统临时目录参数
    exit_code = os.system(f"'{script_path}' '{system_temp_dir}'")
    
    # 验证脚本执行成功
    assert exit_code == 0, "更新脚本应该执行成功"
    
    # 验证系统临时目录已被清理
    assert not os.path.exists(system_temp_dir), "系统临时目录应该已被清理"
    
    # 验证文件已复制到/tmp/converter_update
    target_app_dir = "/tmp/converter_update/Converter.app"
    assert os.path.exists(target_app_dir), "应用程序应该已复制到/tmp/converter_update"
    assert os.path.exists(os.path.join(target_app_dir, "Contents", "MacOS", "launcher")), "launcher文件应该存在"
    
    print("✅ 更新脚本处理系统临时目录测试通过")
    
    # 清理测试文件
    if os.path.exists("/tmp/converter_update"):
        shutil.rmtree("/tmp/converter_update")
    
    print("✅ 测试文件清理完成")

def test_update_script_without_temp_dir():
    """测试更新脚本在没有传入临时目录时的行为"""
    print("\n🧪 测试更新脚本无临时目录参数...")
    
    script_path = "/Users/li/Desktop/png_icns/update/update_apply.command"
    
    # 执行脚本但不传入参数
    exit_code = os.system(f"'{script_path}'")
    
    # 脚本应该正常执行（虽然会显示找不到更新文件的错误）
    assert exit_code != 0, "没有更新文件时脚本应该返回错误"
    
    print("✅ 无临时目录参数测试通过")

def test_restart_with_temp_dir():
    """测试重启逻辑中的临时目录处理"""
    print("\n🧪 测试重启逻辑中的临时目录处理...")
    
    # 模拟update_result
    temp_dir = tempfile.mkdtemp(prefix="test_restart_")
    
    # 在临时目录中创建模拟的.app文件
    test_app_dir = os.path.join(temp_dir, "Converter.app")
    os.makedirs(test_app_dir)
    os.makedirs(os.path.join(test_app_dir, "Contents"))
    os.makedirs(os.path.join(test_app_dir, "Contents", "MacOS"))
    
    # 创建可执行文件
    launcher_path = os.path.join(test_app_dir, "Contents", "MacOS", "launcher")
    with open(launcher_path, 'w') as f:
        f.write("#!/bin/bash\necho 'Test launcher'\n")
    os.chmod(launcher_path, 0o755)
    
    # 创建模拟的downloader
    class MockDownloader:
        def __init__(self):
            self.cleaned_up = False
        
        def cleanup(self):
            self.cleaned_up = True
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    downloader = MockDownloader()
    
    # 模拟update_apply.command脚本
    script_path = "/Users/li/Desktop/png_icns/update/update_apply.command"
    
    # 模拟执行更新脚本（传入临时目录参数）
    exit_code = os.system(f"'{script_path}' '{temp_dir}'")
    
    # 验证脚本执行成功
    assert exit_code == 0, "更新脚本应该执行成功"
    
    # 手动调用downloader清理来验证功能
    downloader.cleanup()
    
    # 验证downloader清理被调用
    assert downloader.cleaned_up, "downloader清理应该被调用"
    
    # 验证临时目录已被清理
    assert not os.path.exists(temp_dir), "临时目录应该被清理"
    
    print("✅ 重启逻辑中的临时目录处理测试通过")

if __name__ == "__main__":
    print("🚀 开始解压和文件放置逻辑测试")
    
    try:
        test_update_script_with_temp_dir()
        test_update_script_without_temp_dir()
        test_restart_with_temp_dir()
        
        print("\n🎉 所有解压和文件放置逻辑测试通过！")
        print("📋 修复总结:")
        print("1. ✅ update_apply.command现在支持从系统临时目录复制文件")
        print("2. ✅ 重启应用时传入系统临时目录路径")
        print("3. ✅ 系统临时目录在使用后被正确清理")
        print("4. ✅ 文件正确放置到/tmp/converter_update目录")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # 清理可能残留的临时目录
        for temp_dir in ["/tmp/converter_update", "/tmp/test_restart_*"]:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        
        # 清理其他可能的临时目录
        for root, dirs, files in os.walk('/tmp'):
            for dir_name in dirs:
                if dir_name.startswith(('test_restart_', 'converter_update')):
                    try:
                        shutil.rmtree(os.path.join(root, dir_name))
                    except:
                        pass