#!/usr/bin/env python3

import platform

# 测试平台检测逻辑
machine = platform.machine().lower()
print(f"机器架构: {machine}")

# 修复后的逻辑
if "arm" in machine:
    platform_str = "arm64"
    print("检测到ARM架构，使用arm64")
elif "x86_64" in machine:
    platform_str = "intel"
    print("检测到x86_64架构，使用intel")
else:
    platform_str = "intel"
    print("未知架构，默认使用intel")

print(f"最终平台字符串: {platform_str}")

# 构建下载URL
tag_name = "2.0.0B1"
download_url = f"https://github.com/pyquick/Converter/releases/download/{tag_name}/Converter_{platform_str}_darwin.zip"
print(f"构建的下载URL: {download_url}")

# 测试URL有效性
import requests
try:
    head_response = requests.head(download_url, timeout=10)
    print(f"URL状态码: {head_response.status_code}")
    if head_response.status_code == 200:
        print("✅ URL有效")
    else:
        print("❌ URL无效")
except Exception as e:
    print(f"❌ 检查URL时出错: {e}")