# -*- coding: utf-8 -*-
import requests
import os
import tempfile
import zipfile
import shutil
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any
# Remove incompatible reconfigure calls for TextIO compatibility
class UpdateDownloader:
    def __init__(self, download_url: str, target_directory: str, progress_callback=None):
        """
        初始化更新下载器
        
        Args:
            download_url: GitHub release页面的URL
            target_directory: 下载文件的目标目录
            progress_callback: 进度回调函数
        """
        self.download_url = download_url
        self.target_directory = target_directory
        self.temp_dir = tempfile.mkdtemp(prefix="update_")
        self.progress_callback = progress_callback
    
    def _extract_download_url(self, tag_name: str) -> Optional[str]:
        """
        从GitHub API获取实际的下载URL
        
        Args:
            tag_name: 版本标签名称（如v2.0.0）
            
        Returns:
            str: 实际的zip文件下载URL，如果提取失败则返回None
        """
        try:
            # 获取平台架构
            import platform
            machine = platform.machine().lower()
            if "arm" in machine:
                platform_str = "arm64"
            elif "x86_64" in machine:
                platform_str = "intel"
            else:
                platform_str = "intel"
            
            # 使用GitHub API获取release信息
            api_url = f"https://api.github.com/repos/pyquick/Converter/releases/tags/{tag_name}"
            response = requests.get(api_url, timeout=10)
            response.encoding = 'utf-8'
            if response.status_code != 200:
                print(f"GitHub API请求失败: {api_url} (状态码: {response.status_code})")
                # 回退到手动构建URL
                download_url = f"https://github.com/pyquick/Converter/releases/download/{tag_name}/Converter_{platform_str}_darwin.zip"
                return download_url
            
            release_data = response.json()
            assets = release_data.get("assets", [])
            
            # 查找匹配平台的文件
            expected_filename = f"Converter_{platform_str}_darwin.zip"
            for asset in assets:
                if asset.get("name") == expected_filename:
                    download_url = asset.get("browser_download_url")
                    if download_url:
                        print(f"找到匹配的下载文件: {expected_filename}")
                        return download_url
            
            # 如果没有找到匹配的文件，回退到手动构建URL
            print(f"未找到匹配的文件 {expected_filename}，使用手动构建URL")
            download_url = f"https://github.com/pyquick/Converter/releases/download/{tag_name}/Converter_{platform_str}_darwin.zip"
            
            # 验证URL是否有效 - 使用GET请求，因为HEAD请求可能被CDN处理不同
            try:
                get_response = requests.get(download_url, timeout=10, stream=True)
                if get_response.status_code == 200:
                    return download_url
                else:
                    print(f"下载URL无效: {download_url} (状态码: {get_response.status_code})")
                    return None
            except requests.exceptions.RequestException:
                # 如果GET请求失败，仍然返回URL让下载过程处理错误
                return download_url
                
        except requests.exceptions.RequestException as e:
            print(f"提取下载URL失败: {e}")
            # 出错时回退到手动构建URL
            import platform
            machine = platform.machine().lower()
            if "arm" in machine:
                platform_str = "arm64"
            elif "x86_64" in machine:
                platform_str = "intel"
            else:
                platform_str = "intel"
            
            download_url = f"https://github.com/pyquick/Converter/releases/download/{tag_name}/Converter_{platform_str}_darwin.zip"
            return download_url
    
    def download_update(self, tag_name: str) -> Dict[str, Any]:
        """
        下载并解压更新文件
        
        Args:
            tag_name: 版本标签名称（如v2.0.0）
            
        Returns:
            dict: 包含下载状态和信息的字典
        """
        try:
            # 提取实际的下载URL
            actual_download_url = self._extract_download_url(tag_name)
            if not actual_download_url:
                return {
                    "status": "error",
                    "message": "无法提取下载链接"
                }
            
            print(f"开始下载更新文件: {actual_download_url}")
            
            # 下载文件到临时目录
            zip_path = os.path.join(self.temp_dir, "update.zip")
            
            # 添加重试机制处理SSL错误
            for attempt in range(3):
                try:
                    response = requests.get(actual_download_url, stream=True, timeout=30)
                    response.raise_for_status()
                    break  # 成功则跳出重试循环
                except requests.exceptions.SSLError as ssl_error:
                    if attempt == 2:  # 最后一次尝试
                        raise ssl_error
                    print(f"SSL错误 (尝试 {attempt + 1}/3): {ssl_error}")
                    time.sleep(2)  # 等待2秒后重试
                except requests.exceptions.RequestException as e:
                    if attempt == 2:  # 最后一次尝试
                        raise e
                    print(f"网络错误 (尝试 {attempt + 1}/3): {e}")
                    time.sleep(2)  # 等待2秒后重试
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # 显示下载进度
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            print(f"下载进度: {progress}% ({downloaded}/{total_size} bytes)",end="\r")
                            # 调用进度回调函数，传递进度、已下载大小和总大小
                            if self.progress_callback:
                                self.progress_callback(progress, downloaded, total_size)
            
            print("下载完成，开始解压...")
            
            # 解压文件
            self._extract_zip(zip_path)
            
            # 应用更新
            self._apply_update()
            
            return {
                "status": "success",
                "message": "更新下载并应用成功",
                "temp_dir": self.temp_dir
            }
            
        except requests.exceptions.RequestException as e:
            # 确保错误消息正确处理非ASCII字符
            try:
                error_message = str(e)
                return {
                    "status": "error",
                    "message": f"下载失败: {error_message}"
                }
            except:
                return {
                    "status": "error",
                    "message": "下载过程中发生编码错误"
                }
        except Exception as e:
            # 确保错误消息正确处理非ASCII字符
            try:
                error_message = str(e)
                return {
                    "status": "error", 
                    "message": f"更新过程中发生错误: {error_message}"
                }
            except:
                return {
                    "status": "error",
                    "message": "处理更新时发生编码错误"
                }
    
    def _extract_zip(self, zip_path: str):
        """解压zip文件到临时目录"""
        with zipfile.ZipFile(zip_path, 'r', metadata_encoding='utf-8') as zip_ref:
            zip_ref.extractall(self.temp_dir)
        print(f"文件解压到: {self.temp_dir}")
    
    def _apply_update(self):
        """应用更新 - 不复制到目标目录，而是准备重启脚本"""
        # 查找解压后的主目录
        extracted_items = os.listdir(self.temp_dir)
        
        # 检查是否有.app文件直接位于临时目录
        app_files = [f for f in extracted_items if f.endswith('.app') and os.path.isdir(os.path.join(self.temp_dir, f))]
        
        if app_files:
            # 如果有.app文件，直接使用临时目录作为源目录
            source_dir = self.temp_dir
        else:
            # 否则查找子目录
            extracted_dirs = [d for d in extracted_items 
                             if os.path.isdir(os.path.join(self.temp_dir, d))]
            
            if not extracted_dirs:
                # 如果没有子目录，直接使用临时目录作为源目录
                source_dir = self.temp_dir
            else:
                # 如果有子目录，使用第一个子目录
                source_dir = os.path.join(self.temp_dir, extracted_dirs[0])
        
        # 创建目标目录（用于存储更新脚本）
        target_com_dir = os.path.expanduser("~/.converter/update/com")
        os.makedirs(target_com_dir, exist_ok=True)
        
        # 复制update_apply.command脚本到目标目录
        script_source = os.path.join(os.path.dirname(__file__), "update_apply.command")
        script_target = os.path.join(target_com_dir, "update_apply.command")
        
        if os.path.exists(script_source):
            shutil.copy2(script_source, script_target)
            # 设置脚本执行权限
            os.chmod(script_target, 0o755)
            print(f"✅ 更新脚本已复制到: {script_target}")
        else:
            print(f"❌ 更新脚本不存在: {script_source}")
        
        print("✅ 更新准备完成，重启时将应用更新")
    
    def cleanup(self):
        """清理临时文件"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"临时文件已清理: {self.temp_dir}")


def download_and_apply_update(update_info: Dict[str, Any], target_directory: str, progress_callback=None) -> Dict[str, Any]:
    """
    下载并应用更新的便捷函数
    
    Args:
        update_info: UpdateManager返回的更新信息字典
        target_directory: 目标安装目录
        progress_callback: 进度回调函数
        
    Returns:
        dict: 下载结果（包含downloader对象用于后续清理）
    """
    download_url = update_info.get("download_url", "")
    latest_version = update_info.get("latest_version", "")
    
    if not download_url or not latest_version:
        return {
            "status": "error",
            "message": "更新信息中缺少必要的URL或版本号"
        }
    
    downloader = UpdateDownloader(download_url, target_directory, progress_callback)
    
    try:
        result = downloader.download_update(latest_version)
        # 将downloader对象添加到结果中，以便调用方可以在适当的时候清理
        result["downloader"] = downloader
        return result
    except Exception as e:
        # 如果出现异常，立即清理
        downloader.cleanup()
        return {
            "status": "error",
            "message": f"下载过程中发生错误: {e}"
        }


if __name__ == "__main__":
    # 测试代码
    test_info = {
        "download_url": "https://github.com/pyquick/converter/releases/tag/v2.0.0",
        "latest_version": "2.0.0"
    }
    
    result = download_and_apply_update(test_info, "./test_update")
    print(f"测试结果: {result}")