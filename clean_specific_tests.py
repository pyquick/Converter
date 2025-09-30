#!/usr/bin/env python3
"""
清理特定测试文件脚本
用于删除指定的测试文件，保留有用的测试目录
"""

import os
import sys

def clean_specific_tests():
    """清理特定的测试文件"""
    
    # 要删除的特定测试文件列表
    test_files_to_delete = [
        "test_user_scenario.py",
        "test_type_annotations.py",
        "test_version_channel_filter.py", 
        "test_real_version_filter.py",
        "test_visual_channel_filter.py",
        "test_beta_mapping_fix.py",
        "test_beta_update_issue.py",
        "test_prerelease_fix.py",
        "test_real_update_manager.py",
        "test_version_mismatch.py",
        "test_visual_update_ui.py",
        "debug_beta_issue.py",
        "debug_tar_bz2.py"
    ]
    
    print("=== 清理特定测试文件 ===")
    deleted_count = 0
    
    for file_name in test_files_to_delete:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                print(f"✅ 删除: {file_name}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ 删除失败 {file_name}: {e}")
        else:
            print(f"⏭️  跳过: {file_name} (不存在)")
    
    print(f"\n=== 清理完成 ===")
    print(f"删除了 {deleted_count} 个测试文件")
    
    return deleted_count

if __name__ == "__main__":
    clean_specific_tests()