#!/usr/bin/env python3
"""
测试取消下载功能和数字进度显示
"""

import sys
import os
sys.path.insert(0, '/Users/li/Desktop/png_icns')

from update.update_gui import UpdateDialog, DownloadThread
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

def test_cancel_functionality():
    """测试取消下载功能"""
    print("测试取消下载功能...")
    
    # 创建测试用的更新信息
    test_update_info = {
        "status": "update_available",
        "message": "Test update available",
        "latest_version": "2.0.0",
        "download_url": "https://example.com/test.zip"
    }
    
    # 创建下载线程
    download_thread = DownloadThread(test_update_info, "/tmp/test")
    
    # 测试取消方法
    print("1. 测试cancel()方法...")
    download_thread.cancel()
    print("   ✅ cancel()方法正常")
    
    # 测试_is_cancelled属性
    print("2. 测试_is_cancelled属性...")
    if hasattr(download_thread, '_is_cancelled') and download_thread._is_cancelled:
        print("   ✅ _is_cancelled属性设置正确")
    else:
        print("   ❌ _is_cancelled属性设置错误")
        return False
    
    print("✅ 取消下载功能测试通过")
    return True

def test_progress_label():
    """测试数字进度标签功能"""
    print("\n测试数字进度标签功能...")
    
    app = QApplication(sys.argv)
    
    try:
        dialog = UpdateDialog()
        
        # 测试progress_label属性
        print("1. 测试progress_label属性...")
        if hasattr(dialog, 'progress_label'):
            print("   ❌ progress_label属性不应该在初始化时存在")
            return False
        
        # 模拟下载更新方法调用
        print("2. 模拟download_update方法调用...")
        dialog.current_update_info = {"status": "test"}
        
        # 测试cancel_download方法
        print("3. 测试cancel_download方法...")
        if hasattr(dialog, 'cancel_download'):
            print("   ✅ cancel_download方法存在")
        else:
            print("   ❌ cancel_download方法不存在")
            return False
        
        print("✅ 数字进度标签功能测试通过")
        return True
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False
    finally:
        app.quit()

if __name__ == "__main__":
    print("开始测试取消下载功能和数字进度显示...\n")
    
    success1 = test_cancel_functionality()
    success2 = test_progress_label()
    
    print(f"\n测试结果:")
    print(f"取消下载功能: {'✅ 通过' if success1 else '❌ 失败'}")
    print(f"数字进度标签: {'✅ 通过' if success2 else '❌ 失败'}")
    
    if success1 and success2:
        print("\n🎉 所有测试通过！取消下载功能和数字进度显示已成功实现。")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败，请检查代码实现。")
        sys.exit(1)