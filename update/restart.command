#!/bin/bash


TARGET_DIR="$HOME/.converter/update/com"
APP_NAME="Converter.app"
echo "🚀 准备重启应用程序..."

# 重启应用程序
sleep 2
open -n "$TARGET_DIR/$APP_NAME"

exit 0