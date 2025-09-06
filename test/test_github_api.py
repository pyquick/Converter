#!/usr/bin/env python3

import requests
import platform

# 测试GitHub API获取下载链接
tag_name = "2.0.0B1"

# 获取平台架构
machine = platform.machine().lower()
if "arm" in machine:
    platform_str = "arm64"
    print("检测到ARM架构，使用arm64")
elif "x86_64" in machine:
    platform_str = "intel"
    print("检测到x86_64架构，使用intel")
else:
    platform_str = "intel"
    print("未知架构，默认使用intel")

print(f"平台字符串: {platform_str}")

# 使用GitHub API获取release信息
api_url = f"https://api.github.com/repos/pyquick/Converter/releases/tags/{tag_name}"
print(f"API URL: {api_url}")

try:
    response = requests.get(api_url, timeout=10,allow_redirects=True,params=None)
    print(f"API响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        release_data = response.json()
        assets = release_data.get("assets", [])
        print(f"找到 {len(assets)} 个assets")
        
        # 查找匹配平台的文件
        expected_filename = f"Converter_{platform_str}_darwin.zip"
        print(f"查找文件: {expected_filename}")
        
        for asset in assets:
            asset_name = asset.get("name")
            download_url = asset.get("browser_download_url")
            print(f"  - {asset_name}: {download_url}")
            
            if asset_name == expected_filename:
                print(f"✅ 找到匹配的文件: {asset_name}")
                print(f"   下载URL: {download_url}")
                break
        else:
            print("❌ 未找到匹配的文件")
            
    else:
        print("❌ API请求失败")
        
except Exception as e:
    print(f"❌ 请求出错: {e}")

# 测试手动构建的URL
manual_url = f"https://github.com/pyquick/Converter/releases/download/{tag_name}/Converter_{platform_str}_darwin.zip"
print(f"\n手动构建URL: {manual_url}")

try:
    head_response = requests.head(manual_url, timeout=10)
    print(f"手动URL状态码: {head_response.status_code}")
    if head_response.status_code == 200:
        print("✅ 手动URL有效")
    else:
        print("❌ 手动URL无效")
except Exception as e:
    print(f"❌ 检查手动URL时出错: {e}")