#!/usr/bin/env python3

import sys
sys.path.insert(0, '/Users/li/Desktop/png_icns')

from update.download_update import UpdateDownloader
import tempfile
import os

def test_download_url_extraction():
    """测试下载URL提取功能"""
    print("测试下载URL提取功能...")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    print(f"临时目录: {temp_dir}")
    
    # 测试下载器
    downloader = UpdateDownloader(
        download_url="https://github.com/pyquick/Converter/releases/tag/2.0.0B1",
        target_directory=temp_dir,
        progress_callback=lambda p: print(f"进度: {p}%")
    )
    
    try:
        # 测试URL提取
        download_url = downloader._extract_download_url("2.0.0B1")
        print(f"提取的下载URL: {download_url}")
        
        if download_url:
            print("✅ URL提取成功")
            
            # 测试URL有效性 - 使用GET请求
            import requests
            try:
                get_response = requests.get(download_url, timeout=10, stream=True)
                print(f"URL状态码: {get_response.status_code}")
                
                if get_response.status_code == 200:
                    print("✅ URL有效")
                else:
                    print("❌ URL无效")
            except Exception as e:
                print(f"❌ URL测试出错: {e}")
                
        else:
            print("❌ URL提取失败")
            
    except Exception as e:
        print(f"❌ 测试出错: {e}")
    finally:
        # 清理
        downloader.cleanup()
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)

if __name__ == "__main__":
    test_download_url_extraction()