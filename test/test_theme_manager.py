#!/usr/bin/env python3
"""
测试优化后的主题管理器功能
"""

import time
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from support.toggle import theme_manager

def test_theme_manager():
    """测试主题管理器功能"""
    print("🚀 启动主题管理器测试...")
    
    # 启动主题管理器
    theme_manager.start()
    
    print("✅ 主题管理器已启动")
    print("📋 当前功能:")
    print("   • 实时系统主题检测 (0.3秒间隔)")
    print("   • 实时应用主题同步 (0.2秒间隔)")
    print("   • 实时系统强调色检测 (0.5秒间隔)")
    print("   • 变化时自动应用主题和颜色")
    
    try:
        # 运行测试一段时间
        print("\n⏰ 测试运行中，请观察系统主题和颜色变化...")
        print("💡 提示: 尝试切换系统主题或更改强调色来测试实时检测功能")
        
        for i in range(10):
            print(f"⏳ 剩余时间: {10 - i}秒")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  用户中断测试")
    
    finally:
        # 停止主题管理器
        theme_manager.stop()
        print("✅ 主题管理器已停止")
        print("🎉 测试完成！")

if __name__ == "__main__":
    test_theme_manager()