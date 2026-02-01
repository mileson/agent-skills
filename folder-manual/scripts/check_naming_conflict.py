#!/usr/bin/env python3
"""
检查文件夹 README 命名冲突，返回唯一文件名

Usage:
    python3 check_naming_conflict.py <project_root> <module_name> <folder_name>

Example:
    python3 check_naming_conflict.py /path/to/project Core Components
    Output: Core_Components_README.md

    # 如果存在同名冲突
    python3 check_naming_conflict.py /path/to/project Core Common
    Output: Views_Core_Common_README.md
"""

import sys
import os
from pathlib import Path


def get_unique_readme_name(project_root: str, module_name: str, folder_name: str) -> str:
    """
    生成唯一的 README 文件名，避免冲突

    命名规则:
    1. 默认: {模块名}_{文件夹名}_README.md
    2. 冲突时: {父文件夹}_{模块名}_{文件夹名}_README.md

    Args:
        project_root: 项目根目录
        module_name: 功能模块名
        folder_name: 文件夹名称

    Returns:
        唯一的 README 文件名
    """
    base_name = f"{module_name}_{folder_name}_README.md"

    # 检查项目中是否存在同名文件
    project_path = Path(project_root)

    # 搜索所有可能的冲突文件
    pattern = f"*_{folder_name}_README.md"
    existing_files = list(project_path.rglob(pattern))

    # 过滤：排除目标文件夹自己的 README（如果是更新操作）
    # 同时排除完全相同的文件名（即当前文件夹自己的 README）
    target_folder = project_path / folder_name
    existing_files = [
        f for f in existing_files
        if f.parent != target_folder and f.name != base_name
    ]

    if not existing_files:
        return base_name

    # 存在冲突，需要添加父文件夹名前缀
    # 获取目标文件夹的父文件夹名称
    if target_folder.exists() or target_folder.parent.exists():
        parent_name = target_folder.parent.name
        # 如果父文件夹是 project_root，则用项目名
        if parent_name == project_path.name:
            parent_name = project_path.name
    else:
        # 文件夹不存在，使用项目根目录名作为前缀
        parent_name = project_path.name

    return f"{parent_name}_{module_name}_{folder_name}_README.md"


def main():
    if len(sys.argv) < 4:
        print("Usage: check_naming_conflict.py <project_root> <module_name> <folder_name>", file=sys.stderr)
        print("", file=sys.stderr)
        print("Arguments:", file=sys.stderr)
        print("  project_root  - Project root directory", file=sys.stderr)
        print("  module_name   - Feature module name (e.g., Core, Feature)", file=sys.stderr)
        print("  folder_name   - Target folder name (e.g., Components, Utils)", file=sys.stderr)
        sys.exit(1)

    project_root = sys.argv[1]
    module_name = sys.argv[2]
    folder_name = sys.argv[3]

    # 验证 project_root 是否存在
    if not os.path.isdir(project_root):
        print(f"Error: Project root directory does not exist: {project_root}", file=sys.stderr)
        sys.exit(1)

    result = get_unique_readme_name(project_root, module_name, folder_name)
    print(result)


if __name__ == "__main__":
    main()
