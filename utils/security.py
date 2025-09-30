#!/usr/bin/env python3
"""
安全工具模块
用于加密和解密敏感信息如GitHub PAT
"""

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecurityManager:
    """安全管理器，用于加密和解密敏感数据"""
    
    def __init__(self):
        self.key_file = os.path.join(os.path.expanduser("~"), ".converter_key")
        self.cipher_suite = self._get_or_create_cipher()
    
    def _get_or_create_cipher(self):
        """获取或创建加密密钥"""
        if os.path.exists(self.key_file):
            # 加载现有密钥
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            # 生成新密钥
            key = Fernet.generate_key()
            # 保存密钥到文件
            os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
            with open(self.key_file, 'wb') as f:
                f.write(key)
            # 设置文件权限为仅用户可读写
            os.chmod(self.key_file, 0o600)
        
        return Fernet(key)
    
    def encrypt_data(self, data: str) -> str:
        """加密字符串数据"""
        if not data:
            return ""
        
        # 将字符串编码为字节
        data_bytes = data.encode('utf-8')
        # 加密数据
        encrypted_bytes = self.cipher_suite.encrypt(data_bytes)
        # 将加密后的字节转换为base64字符串
        encrypted_str = base64.b64encode(encrypted_bytes).decode('utf-8')
        return encrypted_str
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """解密字符串数据"""
        if not encrypted_data:
            return ""
        
        try:
            # 将base64字符串转换为字节
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            # 解密数据
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
            # 将字节转换为字符串
            decrypted_str = decrypted_bytes.decode('utf-8')
            return decrypted_str
        except Exception as e:
            print(f"解密失败: {e}")
            return ""
    
    def reset_key(self):
        """重置加密密钥（会失效所有已加密的数据）"""
        if os.path.exists(self.key_file):
            os.remove(self.key_file)
        self.cipher_suite = self._get_or_create_cipher()
        print("加密密钥已重置")

# 全局安全管理器实例
security_manager = SecurityManager()

def encrypt_pat(pat: str) -> str:
    """加密PAT"""
    return security_manager.encrypt_data(pat)

def decrypt_pat(encrypted_pat: str) -> str:
    """解密PAT"""
    return security_manager.decrypt_data(encrypted_pat)

def test_encryption():
    """测试加密功能"""
    test_pat = "ghp_test123456789"
    print("原始PAT:", test_pat)
    
    # 加密
    encrypted = encrypt_pat(test_pat)
    print("加密后:", encrypted)
    
    # 解密
    decrypted = decrypt_pat(encrypted)
    print("解密后:", decrypted)
    
    # 验证
    if test_pat == decrypted:
        print("✅ 加密解密测试通过")
    else:
        print("❌ 加密解密测试失败")

if __name__ == "__main__":
    test_encryption()