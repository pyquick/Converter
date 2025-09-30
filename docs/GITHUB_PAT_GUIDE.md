# GitHub PAT功能使用指南

## 概述

GitHub PAT (Personal Access Token) 功能允许用户通过输入个人访问令牌来访问GitHub API，提高API调用的限制和安全性。PAT会被加密存储，确保安全性。

## 功能特性

- ✅ **安全加密**: PAT使用强加密算法进行加密存储
- ✅ **设置界面**: 在通用设置中提供PAT输入界面
- ✅ **实时测试**: 提供PAT有效性测试功能
- ✅ **自动使用**: 更新管理器自动使用PAT进行GitHub API调用
- ✅ **错误处理**: 完善的错误处理和用户反馈

## 使用方法

### 1. 创建GitHub PAT

1. 访问 [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. 点击 "Generate new token"
3. 设置token名称（如：Converter Tool）
4. 选择过期时间（建议90天或更长）
5. 选择权限范围（建议只勾选 `repo` 权限）
6. 点击 "Generate token"
7. **立即复制token**，因为只会显示一次

### 2. 在设置中配置PAT

1. 打开Converter工具
2. 进入设置界面（Settings）
3. 切换到 "General" 标签页
4. 找到 "GitHub设置" 部分
5. 在输入框中粘贴您的PAT
6. 点击 "测试PAT" 按钮验证有效性
7. 关闭设置窗口时PAT会自动加密保存

### 3. 验证PAT功能

运行测试脚本来验证PAT功能：

```bash
python3.13 test_github_pat.py
```

### 4. 使用演示界面

运行演示脚本来体验PAT设置界面：

```bash
python3.13 demo_pat_settings.py
```

## 安全说明

### 加密存储
- PAT使用Fernet对称加密算法进行加密
- 加密密钥存储在用户主目录的 `.converter_key` 文件中
- 密钥文件权限设置为仅用户可读写（600）

### PAT安全建议
- 只授予必要的权限（建议只勾选 `repo`）
- 设置合理的过期时间
- 不要在代码中硬编码PAT
- 定期更新PAT
- 如果PAT泄露，立即在GitHub上删除并重新生成

### 显示安全
- 在界面中PAT以密码形式显示（隐藏字符）
- 状态显示时PAT部分被隐藏（如：`ghp_Z5PQ****q23ZSBpC`）
- 提供清除按钮方便删除PAT

## API使用

### 在更新管理器中使用

更新管理器会自动检测和使用已保存的PAT：

```python
from update.update_manager import UpdateManager

update_manager = UpdateManager("1.0.0")
pat = update_manager.get_github_pat()  # 获取解密后的PAT

# 检查更新时会自动使用PAT
result = update_manager.check_for_updates("1.0.0", "Stable")
```

### 手动获取PAT

```python
from PySide6.QtCore import QSettings
from utils.security import decrypt_pat

settings = QSettings("pyquick", "converter")
encrypted_pat = settings.value("general/github_pat", "", type=str)
if encrypted_pat:
    pat = decrypt_pat(encrypted_pat)
    # 使用pat进行GitHub API调用
```

## 故障排除

### PAT测试失败
- 检查PAT是否正确复制（没有多余空格）
- 检查PAT是否过期
- 检查网络连接
- 检查是否勾选了必要的权限

### 加密/解密失败
- 检查是否有权限访问 `.converter_key` 文件
- 尝试重置加密密钥（会清除所有加密数据）

```python
from utils.security import security_manager
security_manager.reset_key()
```

### API调用限制
- 未认证的API调用限制为每小时60次
- 使用PAT的API调用限制为每小时5000次
- 如果达到限制，请稍后再试

## 相关文件

- `utils/security.py` - 加密解密功能
- `settings/general_settings.py` - PAT设置界面
- `update/update_manager.py` - 更新管理器PAT使用
- `test_github_pat.py` - 功能测试脚本
- `demo_pat_settings.py` - 设置界面演示

## 更新日志

- **2024-01-XX**: 初始实现GitHub PAT功能
  - 添加安全加密存储
  - 集成到设置界面
  - 集成到更新管理器
  - 添加测试和演示功能