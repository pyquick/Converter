#!/usr/bin/env python3
"""
集成测试：验证临时文件清理时机修复
"""

import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, MagicMock, patch

# 添加项目路径到sys.path
sys.path.insert(0, '/Users/li/Desktop/png_icns')

from update.download_update import download_and_apply_update
from update.update_gui import UpdateDialog

def test_complete_update_flow():
    """测试完整的更新流程，验证临时文件在重启时才被清理"""
    print("🧪 测试完整更新流程...")
    
    # 创建模拟的更新信息
    update_info = {
        "download_url": "http://example.com/test.zip",
        "latest_version": "1.0.0",
        "message": "Update available"
    }
    
    # 创建模拟的下载结果
    mock_result = {
        "status": "success",
        "message": "Download successful",
        "temp_dir": tempfile.mkdtemp(prefix="integration_test_")
    }
    
    # 在临时目录中创建一些测试文件
    test_file = os.path.join(mock_result["temp_dir"], "test.app")
    with open(test_file, 'w') as f:
        f.write("test application content")
    
    print(f"📁 创建测试临时目录: {mock_result['temp_dir']}")
    print(f"📄 创建测试文件: {test_file}")
    
    # 验证临时目录和文件存在
    assert os.path.exists(mock_result["temp_dir"]), "临时目录应该存在"
    assert os.path.exists(test_file), "测试文件应该存在"
    
    # 创建模拟的downloader对象
    class MockDownloader:
        def __init__(self):
            self.cleaned_up = False
        
        def cleanup(self):
            self.cleaned_up = True
            if os.path.exists(mock_result["temp_dir"]):
                shutil.rmtree(mock_result["temp_dir"])
    
    mock_downloader = MockDownloader()
    mock_result["downloader"] = mock_downloader
    
    # 使用不同的变量名来避免冲突
    mock_downloader_class = MockDownloader
    download_module.UpdateDownloader = mock_downloader_class
    
    # 创建UpdateDialog实例
    dialog = UpdateDialog()
    dialog.update_result = mock_result
    
    # 模拟update_apply.command脚本
    update_script_path = os.path.expanduser("~/.converter/update/com/update_apply.command")
    os.makedirs(os.path.dirname(update_script_path), exist_ok=True)
    
    with open(update_script_path, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("echo 'Update script executed'\n")
    os.chmod(update_script_path, 0o755)
    
    print(f"📜 创建更新脚本: {update_script_path}")
    
    # 验证脚本存在且有执行权限
    assert os.path.exists(update_script_path), "更新脚本应该存在"
    assert os.access(update_script_path, os.X_OK), "更新脚本应该有执行权限"
    
    # 验证临时目录在重启前仍然存在
    assert os.path.exists(mock_result["temp_dir"]), "重启前临时目录应该存在"
    assert not mock_downloader.cleaned_up, "重启前downloader不应该被清理"
    
    print("✅ 重启前验证通过：临时文件未被清理")
    
    # 模拟执行restart_application方法
    with patch('os.system') as mock_system, \
         patch('os.QApplication.quit') as mock_quit:
        
        dialog.restart_application()
        
        # 验证os.system被调用（执行更新脚本）
        mock_system.assert_called_once()
        call_args = mock_system.call_args[0][0]
        assert update_script_path in call_args, "应该调用更新脚本"
        
        # 验证downloader.cleanup被调用
        assert mock_downloader.cleaned_up, "downloader应该已被清理"
        
        # 验证临时目录已被清理
        assert not os.path.exists(mock_result["temp_dir"]), "重启后临时目录应该已被清理"
        
        # 验证QApplication.quit被调用
        mock_quit.assert_called_once()
    
    print("✅ 重启后验证通过：临时文件已被正确清理")
    
    # 清理测试脚本
    if os.path.exists(update_script_path):
        os.remove(update_script_path)
    script_dir = os.path.dirname(update_script_path)
    if os.path.exists(script_dir) and not os.listdir(script_dir):
        os.rmdir(script_dir)
    
    print("✅ 完整更新流程测试通过")

def test_invalid_temp_dir_handling():
    """测试无效临时目录的处理"""
    print("\n🧪 测试无效临时目录处理...")
    
    dialog = UpdateDialog()
    
    # 测试1: 不存在的临时目录
    dialog.update_result = {
        "temp_dir": "/nonexistent/path"
    }
    
    # 模拟状态标签设置
    original_set_text = dialog.update_status_label.setText
    status_messages = []
    
    def mock_set_text(text):
        status_messages.append(text)
        original_set_text(text)
    
    dialog.update_status_label.setText = mock_set_text
    
    dialog.restart_application()
    
    # 验证显示了正确的错误消息
    assert any("更新文件路径无效" in msg for msg in status_messages), "应该显示路径无效错误"
    
    print("✅ 不存在临时目录处理测试通过")
    
    # 测试2: 空的临时目录
    dialog.update_result = {
        "temp_dir": ""
    }
    
    status_messages.clear()
    dialog.restart_application()
    
    assert any("更新文件路径无效" in msg for msg in status_messages), "应该显示路径无效错误"
    
    print("✅ 空临时目录处理测试通过")
    
    # 测试3: 模拟错误处理的downloader类
    class ErrorDownloader:
        def __init__(self):
            self.cleaned_up = False
        
        def cleanup(self):
            self.cleaned_up = True
            # 故意不清理临时目录来测试错误处理
    
    # 使用不同的变量名来避免冲突
    error_downloader_class = ErrorDownloader
    download_module.UpdateDownloader = error_downloader_class
    
    # 测试4: 没有update_result属性
    if hasattr(dialog, 'update_result'):
        delattr(dialog, 'update_result')
    
    status_messages.clear()
    dialog.restart_application()
    
    assert any("更新信息丢失" in msg for msg in status_messages), "应该显示信息丢失错误"
    
    print("✅ 无update_result处理测试通过")

if __name__ == "__main__":
    print("🚀 开始集成测试：临时文件清理时机修复")
    
    try:
        test_complete_update_flow()
        test_invalid_temp_dir_handling()
        
        print("\n🎉 所有集成测试通过！临时文件清理时机修复成功")
        
    except Exception as e:
        print(f"\n❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # 清理可能残留的临时目录
        temp_dirs = []
        for root, dirs, files in os.walk('/tmp'):
            for dir_name in dirs:
                if dir_name.startswith('integration_test_'):
                    temp_dirs.append(os.path.join(root, dir_name))
        
        for temp_dir in temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    print(f"🧹 清理残留临时目录: {temp_dir}")
            except Exception as e:
                print(f"⚠️  清理临时目录失败 {temp_dir}: {e}")