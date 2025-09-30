# TODO List

## New Features:
1. ✅ GitHub PAT (Personal Access Token) 支持
   - ✅ 添加PAT输入界面到通用设置
   - ✅ 实现PAT加密存储
   - ✅ 在更新管理器中使用PAT进行GitHub API调用
   - ✅ 添加PAT安全机制

2. xxx

## Bug Fixes:
1. xxx

## Improvements:
1. xxx

---

## Alpha/Deepdev版本通道过滤 - ✅ 已完成

### 目标
实现对Alpha和Deepdev版本的特殊处理，确保内部版本只显示对应的更新通道，提升用户体验和版本管理的准确性。

### 具体任务
1. **版本类型检测** - ✅ 已完成
   - 在UpdateManager中增强版本解析功能
   - 识别版本号中的Alpha(A)和Deepdev(D)标识
   - 将Alpha/D版本标记为内部版本

2. **通道过滤逻辑** - ✅ 已完成
   - Alpha版本仅显示"Alpha"和"Stable"通道
   - Deepdev版本仅显示"Deepdev"和"Stable"通道
   - 普通版本显示所有5个通道(Beta, Alpha, Deepdev, RC, Stable)

3. **参数映射调整** - ✅ 已完成
   - 内部版本使用简化索引映射(0: Alpha, 1: Stable)
   - 普通版本保持原有映射(0: Beta, 1: Alpha, 2: Deepdev, 3: RC, 4: Stable)

### 技术实现
- **版本解析增强**: 在`UpdateManager._parse_version()`中增加对Alpha和Deepdev标签的识别
- **内部版本判断**: 添加`is_internal_version()`方法判断版本类型
- **通道过滤**: 在UI层根据版本类型过滤显示的更新通道
- **参数映射**: 根据版本类型调整`prerelease_types`数组的索引映射

### 测试结果
- ✅ 版本检测功能正确识别Alpha/D版本为内部版本
- ✅ 通道过滤逻辑对Alpha/D版本仅显示对应通道
- ✅ 参数映射逻辑正确处理不同版本类型的索引选择
- ✅ 真实环境测试验证功能正确性

### 完成状态
- 功能实现: ✅ 完成
- 单元测试: ✅ 通过
- 集成测试: ✅ 通过
- 文档更新: ✅ 完成

---

## 之前的任务记录...

### 设置合并 - ✅ 已完成
将图像转换器设置合并到通用设置中，简化设置界面结构。

### Update Command Script Not Found - ✅ 已修复
修复了更新命令脚本找不到的问题，确保更新功能正常运行。

### Pre-release版本支持 - ✅ 已完成
实现了对预发布版本的支持，包括版本解析、更新检查和用户界面显示。

### 更新通道UI优化 - ✅ 已完成
优化了更新通道的用户界面，提供更好的用户体验和版本选择功能。

### Beta版本更新检查问题分析 - ✅ 已完成
分析并解决了Beta版本更新检查中的问题，确保更新功能的稳定性和准确性。