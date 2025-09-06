#!/bin/bash

# 更新应用脚本 - 不复制到/Applications，而是直接重启
# 将更新文件复制到 ~/.converter/update/com/ 目录

# 设置变量
TEMP_DIR="/tmp/converter_update"
TARGET_DIR="$HOME/.converter/update/com"
APP_NAME="Converter.app"

# 创建目标目录
mkdir -p "$TARGET_DIR"

# 检查是否有系统临时目录传入
if [ -n "$1" ] && [ -d "$1" ]; then
    # 使用传入的临时目录
    SYSTEM_TEMP_DIR="$1"
    echo "📦 使用系统临时目录: $SYSTEM_TEMP_DIR"
    
    # 复制系统临时目录内容到TEMP_DIR
    echo "📋 复制更新文件到 $TEMP_DIR..."
    mkdir -p "$TEMP_DIR"
    cp -R "$SYSTEM_TEMP_DIR/"* "$TEMP_DIR/" 2>/dev/null || true
    
    # 清理系统临时目录
    rm -rf "$SYSTEM_TEMP_DIR"
    echo "✅ 系统临时目录已清理"
else
    # 检查临时目录是否存在
    if [ ! -d "$TEMP_DIR" ]; then
        echo "❌ 临时更新目录不存在: $TEMP_DIR,需要创建临时目录"
        mkdir -p "$TEMP_DIR"
    fi
fi

# 查找解压后的应用程序
EXTRACTED_DIRS=($(find "$TEMP_DIR" -maxdepth 1 -type d -name "*.app"))

if [ ${#EXTRACTED_DIRS[@]} -eq 0 ]; then
    echo "❌ 在临时目录中未找到应用程序"
    exit 1
fi

# 获取第一个找到的.app目录
SOURCE_APP="${EXTRACTED_DIRS[0]}"
echo "📦 找到更新应用程序: $SOURCE_APP"

# 设置可执行文件权限
echo "🔧 设置可执行文件权限..."
find "$SOURCE_APP" -name "*.app" -exec chmod -R 755 {} \;
find "$SOURCE_APP" -path "*/Contents/MacOS/*" -exec chmod +x {} \;

# 特别设置launcher可执行文件权限
if [ -f "$SOURCE_APP/Contents/MacOS/launcher" ]; then
    chmod +x "$SOURCE_APP/Contents/MacOS/launcher"
    echo "✅ 设置 launcher 可执行权限"
fi

# 删除目标目录中的旧程序
echo "🗑️  清理目标目录..."
rm -rf "$TARGET_DIR/$APP_NAME"

# 复制新程序到目标目录
echo "📋 复制新应用程序到 $TARGET_DIR..."
cp -R "$SOURCE_APP" "$TARGET_DIR/"

# 再次确保权限正确
chmod -R 755 "$TARGET_DIR/$APP_NAME"
find "$TARGET_DIR/$APP_NAME" -path "*/Contents/MacOS/*" -exec chmod +x {} \;

if [ -f "$TARGET_DIR/$APP_NAME/Contents/MacOS/launcher" ]; then
    chmod +x "$TARGET_DIR/$APP_NAME/Contents/MacOS/launcher"
fi

echo "✅ 更新完成！应用程序已复制到: $TARGET_DIR/$APP_NAME"
echo "🚀 准备重启应用程序..."

# 重启应用程序
sleep 2
open -n "$TARGET_DIR/$APP_NAME"

exit 0