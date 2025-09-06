#!/usr/bin/env python3
"""
测试更新功能修复
验证Converter.app文件在解压后不会丢失
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from update.download_update import UpdateDownloader

def test_update_extraction():
    """测试更新文件解压和应用"""
    print("=== 测试更新文件解压功能 ===")
    
    # 创建测试目录结构
    test_target_dir = "./test_update_target"
    os.makedirs(test_target_dir, exist_ok=True)
    
    # 创建模拟的Converter.app目录结构
    test_app_dir = "./Converter.app"
    os.makedirs(test_app_dir, exist_ok=True)
    
    # 在app目录中创建一些文件
    os.makedirs(os.path.join(test_app_dir, "Contents", "MacOS"), exist_ok=True)
    
    with open(os.path.join(test_app_dir, "Contents", "Info.plist"), "w") as f:
        f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
    
    with open(os.path.join(test_app_dir, "Contents", "MacOS", "Converter"), "w") as f:
        f.write("#!/bin/bash\necho 'Test Converter App'")
    os.chmod(os.path.join(test_app_dir, "Contents", "MacOS", "Converter"), 0o755)
    
    # 创建zip文件
    import zipfile
    zip_path = "./test_update.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        # 添加app目录，确保在zip的根目录
        for root, dirs, files in os.walk(test_app_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, ".")
                zipf.write(file_path, arcname)
    
    print(f"创建测试zip文件: {zip_path}")
    
    # 测试UpdateDownloader
    downloader = UpdateDownloader("", test_target_dir)
    
    # 手动调用解压和应用方法
    try:
        # 解压文件
        downloader._extract_zip(zip_path)
        
        # 应用更新
        downloader._apply_update()
        

        
        # 检查目标目录中是否有Converter.app
        target_app_path = os.path.join(test_target_dir, "Converter.app")
        if os.path.exists(target_app_path):
            print("✅ Converter.app文件成功复制到目标目录")
            
            # 检查文件内容
            if os.path.exists(os.path.join(target_app_path, "Contents", "MacOS", "Converter")):
                print("✅ 应用程序二进制文件存在")
            else:
                print("❌ 应用程序二进制文件缺失")
                
        else:
            print("❌ Converter.app文件未复制到目标目录")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
    
    finally:
        # 清理测试文件
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists(test_target_dir):
            shutil.rmtree(test_target_dir)
        if os.path.exists(test_app_dir):
            shutil.rmtree(test_app_dir)
        downloader.cleanup()
    
    print("=== 测试完成 ===")

if __name__ == "__main__":
    import sys
    test_update_extraction()