#!/usr/bin/env python3
"""
检测项目模式：Greenfield（从0到1）或 Brownfield（系统迭代）

使用方法:
    python3 detect_project_mode.py [--workspace PATH]
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional


def detect_project_mode(workspace_path: str) -> Dict:
    """
    检测项目模式
    
    参数:
        workspace_path: 工作空间路径
    
    返回:
        {
            "mode": "greenfield" | "brownfield",
            "hasDocStructure": bool,
            "existingDocs": dict,
            "existingFeatureList": str | None
        }
    """
    doc_path = Path(workspace_path) / "doc"
    
    result = {
        "mode": "greenfield",
        "hasDocStructure": False,
        "existingDocs": {},
        "existingFeatureList": None
    }
    
    # 检查 doc/ 目录是否存在
    if not doc_path.exists():
        return result
    
    # 检测到 doc/ 目录存在
    result["hasDocStructure"] = True
    
    # 扫描已有文档结构
    doc_folders = {
        "01_PRD": "prd",
        "02_arch": "arch",
        "03_database": "database",
        "04_api": "api",
        "05_implementation": "implementation",
        "07_testing": "testing"
    }
    
    for folder_name, key in doc_folders.items():
        folder_path = doc_path / folder_name
        if folder_path.exists() and folder_path.is_dir():
            md_files = [f.name for f in folder_path.glob("*.md")]
            sql_files = [f.name for f in folder_path.glob("*.sql")]
            all_files = md_files + sql_files
            if all_files:
                result["existingDocs"][key] = all_files
    
    # 检查 feature_list.json
    feature_list_path = doc_path / "06_dev-logs" / "feature_list.json"
    if feature_list_path.exists():
        result["existingFeatureList"] = str(feature_list_path)
        result["mode"] = "brownfield"  # 有功能清单 = 迭代模式
    
    return result


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="检测项目模式")
    parser.add_argument(
        "--workspace",
        type=str,
        default=".",
        help="工作空间路径（默认: 当前目录）"
    )
    
    args = parser.parse_args()
    
    # 检测模式
    result = detect_project_mode(args.workspace)
    
    # 输出结果
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 输出模式提示
    if result["mode"] == "greenfield":
        print("\n✅ 检测到 Greenfield 模式（从0到1全新项目开发）", file=sys.stderr)
        print("   建议阅读：references/greenfield/", file=sys.stderr)
    else:
        print("\n✅ 检测到 Brownfield 模式（基于已有系统的迭代优化）", file=sys.stderr)
        print("   建议阅读：references/brownfield/", file=sys.stderr)
        print(f"   现有文档：{len(result['existingDocs'])} 个目录", file=sys.stderr)


if __name__ == "__main__":
    main()
