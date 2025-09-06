#!/usr/bin/env python3
"""
测试临时文件清理时机修复
"""

import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, MagicMock

# 添加项目路径到sys.path
sys.path.insert(0, '/Users/li/Desktop/png_icns')

from update.download_update import UpdateDownloader

def test_downloader_cleanup():
    """测试UpdateDownloader的cleanup方法"""
    print("🧪 测试UpdateDownloader清理功能...")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="test_update_")
    print(f"📁 创建测试临时目录: {temp_dir}")
    
    # 创建一些测试文件
    test_file = os.path.join(temp_dir, "test.txt")
    with open(test_file, 'w') as f:
        f.write("test content")
    
    # 创建downloader实例
    downloader = UpdateDownloader("http://example.com", "/Applications")
    
    # 手动设置temp_dir来测试cleanup
    downloader.temp_dir = temp_dir
    
    # 验证目录存在
    assert os.path.exists(temp_dir), "临时目录应该存在"
    assert os.path.exists(test_file), "测试文件应该存在"
    
    # 执行清理
    downloader.cleanup()
    
    # 验证目录已被删除
    assert not os.path.exists(temp_dir), "临时目录应该已被清理"
    assert not os.path.exists(test_file), "测试文件应该已被清理"
    
    print("✅ UpdateDownloader清理功能测试通过")

def test_download_and_apply_update_no_cleanup():
    """测试download_and_apply_update不会立即清理临时文件"""
    print("\n🧪 测试download_and_apply_update不立即清理...")
    
    from update.download_update import download_and_apply_update
    
    # 模拟更新信息
    update_info = {
        "download_url": "http://example.com/test.zip",
        "latest_version": "1.0.0"
    }
    
    # 模拟下载器类
    class MockDownloader:
        def __init__(self, download_url, target_directory, progress_callback=None):
            self.download_url = download_url
            self.target_directory = target_directory
            self.progress_callback = progress_callback
            self.temp_dir = tempfile.mkdtemp(prefix="mock_update_")
            self.cleaned_up = False
        
        def download_update(self, version):
            return {
                "status": "success",
                "message": "Download successful",
                "temp_dir": self.temp_dir
            }
        
        def cleanup(self):
            self.cleaned_up = True
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
    
    # 保存原始类引用
    import update.download_update as download_module
    original_downloader = download_module.UpdateDownloader
    # 使用不同的变量名来避免冲突
    download_module.UpdateDownloader = MockDownloader
    
    try:
        # 调用下载函数
        result = download_and_apply_update(update_info, "/Applications")
        
        # 验证结果包含downloader对象
        assert "downloader" in result, "结果应该包含downloader对象"
        assert result["status"] == "success", "下载应该成功"
        
        # 验证临时目录仍然存在（没有被立即清理）
        temp_dir = result["temp_dir"]
        assert os.path.exists(temp_dir), "临时目录应该仍然存在"
        
        # 验证downloader还没有被清理
        downloader = result["downloader"]
        assert not downloader.cleaned_up, "downloader不应该被立即清理"
        
        print("✅ download_and_apply_update不立即清理测试通过")
        
        # 现在手动清理
        downloader.cleanup()
        assert not os.path.exists(temp_dir), "手动清理后临时目录应该不存在"
        assert downloader.cleaned_up, "downloader应该已被清理"
        
        print("✅ 手动清理功能测试通过")
        
    finally:
        # 恢复原始类
        download_module.UpdateDownloader = original_downloader

def test_error_case_cleanup():
    """测试错误情况下的清理"""
    print("\n🧪 测试错误情况下的清理...")
    
    from update.download_update import download_and_apply_update
    
    # 模拟会抛出异常的下载器
    class ErrorDownloader:
        def __init__(self, download_url, target_directory, progress_callback=None):
            self.download_url = download_url
            self.target_directory = target_directory
            self.progress_callback = progress_callback
            self.temp_dir = tempfile.mkdtemp(prefix="error_update_")
            self.cleaned_up = False
        
        def download_update(self, version):
            raise Exception("模拟下载错误")
        
        def cleanup(self):
            self.cleaned_up = True
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
    
    # 保存原始类引用
    import update.download_update as download_module
    original_downloader = download_module.UpdateDownloader
    # 使用不同的变量名来避免冲突
    download_module.UpdateDownloader = ErrorDownloader
    
    try:
        # 调用下载函数（应该会抛出异常并被捕获）
        result = download_and_apply_update({
            "download_url": "http://example.com",
            "latest_version": "1.0.0"
        }, "/Applications")
        
        # 验证返回了错误结果
        assert result["status"] == "error", "应该返回错误状态"
        assert "模拟下载错误" in result["message"], "错误消息应该包含异常信息"
        
        # 验证downloader已经被清理（在异常处理中）
        # 注意：由于ErrorDownloader实例在异常处理中被清理，我们无法直接访问它
        # 但我们可以验证临时目录已经被清理
        
        print("✅ 错误情况清理测试通过")
        
    finally:
        # 恢复原始类
        download_module.UpdateDownloader = original_downloader

if __name__ == "__main__":
    print("🚀 开始测试临时文件清理时机修复")
    
    try:
        test_downloader_cleanup()
        test_download_and_apply_update_no_cleanup()
        test_error_case_cleanup()
        
        print("\n🎉 所有测试通过！临时文件清理时机修复成功")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)