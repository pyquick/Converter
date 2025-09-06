#!/usr/bin/env python3

import requests

# 测试不同的URL格式
url1 = "https://github.com/pyquick/Converter/releases/download/2.0.0B1/Converter_intel_darwin.zip"
url2 = "https://github.com/pyquick/Converter/releases/download/2.0.0B1/Converter_intel_darwin.zip?raw=true"

print("测试URL重定向:")
print(f"URL 1: {url1}")

try:
    response = requests.head(url1, timeout=10, allow_redirects=True)
    print(f"URL 1 最终状态码: {response.status_code}")
    print(f"URL 1 最终URL: {response.url}")
    print(f"URL 1 重定向次数: {len(response.history)}")
    for i, redirect in enumerate(response.history):
        print(f"  重定向 {i+1}: {redirect.status_code} -> {redirect.url}")
except Exception as e:
    print(f"URL 1 错误: {e}")

print(f"\nURL 2: {url2}")

try:
    response = requests.head(url2, timeout=10, allow_redirects=True)
    print(f"URL 2 最终状态码: {response.status_code}")
    print(f"URL 2 最终URL: {response.url}")
    print(f"URL 2 重定向次数: {len(response.history)}")
    for i, redirect in enumerate(response.history):
        print(f"  重定向 {i+1}: {redirect.status_code} -> {redirect.url}")
except Exception as e:
    print(f"URL 2 错误: {e}")

# 测试GitHub API返回的URL
print("\n测试GitHub API返回的URL:")
api_url = "https://api.github.com/repos/pyquick/Converter/releases/tags/2.0.0B1"
try:
    response = requests.get(api_url, timeout=10)
    if response.status_code == 200:
        data = response.json()
        for asset in data.get("assets", []):
            if "intel" in asset.get("name", ""):
                api_download_url = asset.get("browser_download_url")
                print(f"API下载URL: {api_download_url}")
                
                # 测试这个URL
                response = requests.head(api_download_url, timeout=10, allow_redirects=True)
                print(f"API URL 最终状态码: {response.status_code}")
                print(f"API URL 最终URL: {response.url}")
                break
    else:
        print(f"API请求失败: {response.status_code}")
except Exception as e:
    print(f"API测试错误: {e}")