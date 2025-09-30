# PNG/ICNS Converter Application

## Overview
A modern desktop application for converting PNG images to ICNS format (macOS icons) with additional archive management functionality.

## Features
- PNG to ICNS conversion
- Archive management (ZIP handling)
- Modern UI with QFluentWidgets
- Theme support (Light/Dark/Auto)
- Settings management
- Debug logging support
- **NEW: Animated app launching with fade in/out effects**

## Project Structure
- `Converter.py` - Main application entry point and UI
- `image_converter.py` - PNG to ICNS conversion functionality
- `arc_gui.py` - Archive management functionality
- `support/` - Supporting modules (themes, settings, debug logging)
- `test/` - Test files

## Requirements
- Python 3.13
- PySide6
- QFluentWidgets
- Pillow (PIL)

## Usage
```bash
pip3.13 install -r requirements.txt
python3 Converter.py
```

## Recent Updates

### 动态效果实现总结

#### New Features:
1. 实现了AnimatedAppDialog基类，提供淡入淡出动画效果
2. 创建了ImageAppDialog类，用于Image Converter应用的动画启动
3. 创建了ZipAppDialog类，用于Archive Manager应用的动画启动
4. 实现了多进程启动外部应用的功能
5. 添加了加载指示器(IndeterminateProgressBar)提升用户体验

#### Bug Fixes:
1. 修复了重复的ZipAppDialog类定义问题
2. 修复了ImageAppDialog类缺失的问题
3. 修复了run_image_app和run_zip_app函数中的主窗口检测逻辑
4. 修复了AttributeError: 'IconButtonsWindow' object has no attribute 'run_image_app'错误

#### Improvements:
1. 优化了动画对话框的UI布局，添加了标题和加载指示器
2. 实现了主窗口检测机制，通过遍历QApplication.topLevelWidgets()查找IconButtonsWindow实例
3. 添加了异常处理和回退机制，确保在主窗口未找到时仍能启动应用
4. 优化了动画时序，对话框显示后300ms启动外部应用，1秒后自动关闭
5. 统一了动画风格，使用QPropertyAnimation实现平滑的淡入淡出效果

#### 技术实现:
- 使用QPropertyAnimation控制窗口透明度实现淡入淡出效果
- 使用QTimer.singleShot实现延迟启动和自动关闭
- 使用multiprocessing.Process在独立进程中运行外部应用
- 使用IndeterminateProgressBar提供视觉反馈
- 遵循PySide6编码规范，使用类型注解和文档字符串