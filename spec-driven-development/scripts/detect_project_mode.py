#!/usr/bin/env python3
"""
检测项目模式：Greenfield（从0到1）或 Brownfield（系统迭代）

使用方法:
    python3 detect_project_mode.py [--workspace PATH]
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict


def is_folder_manual_file(path: Path) -> bool:
    """判断是否为文件夹说明书。"""
    return path.name == "README.md" or path.name.endswith("_README.md")


def parse_doc_version(content: str) -> float:
    """从 Markdown 内容中提取文档版本。"""
    match = re.search(r"\*\*文档版本\*\*[：:]\s*v?(\d+\.\d+)", content)
    return float(match.group(1)) if match else 0.0


def count_revision_rows(content: str) -> int:
    """统计修订历史行数。"""
    pattern = r"^\|\s*v\d+\.\d+\s*\|"
    return len(re.findall(pattern, content, flags=re.MULTILINE))


def has_versioned_execution_tracking(doc_path: Path) -> bool:
    """是否存在版本化执行跟踪，且不是初始 v1.0 单骨架。"""
    tracking_files = sorted((doc_path / "DevLogs").glob("v*_执行跟踪.md"))
    if not tracking_files:
        return False
    if len(tracking_files) > 1:
        return True
    return tracking_files[0].name != "v1.0_执行跟踪.md"


def is_incremental_project(doc_path: Path) -> bool:
    """根据正式文档版本、修订历史和执行跟踪判断是否为 Brownfield。"""
    if has_versioned_execution_tracking(doc_path):
        return True

    for md_file in doc_path.rglob("*.md"):
        if is_folder_manual_file(md_file):
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
        except OSError:
            continue

        if parse_doc_version(content) > 1.0:
            return True
        if count_revision_rows(content) > 1:
            return True

    return False


def detect_project_mode(workspace_path: str) -> Dict:
    """检测项目模式。"""
    workspace = Path(workspace_path)
    doc_path = None
    for candidate in ("Documentation", "doc"):
        candidate_path = workspace / candidate
        if candidate_path.exists():
            doc_path = candidate_path
            break

    result = {
        "mode": "greenfield",
        "hasDocStructure": False,
        "existingDocs": {},
        "existingFeatureList": None,
        "documentationRoot": "Documentation",
    }

    if doc_path is None:
        return result

    result["hasDocStructure"] = True
    result["documentationRoot"] = doc_path.name

    doc_folders = {
        "Basic": "basic",
        "Framework": "framework",
        "Modules": "modules",
        "DevLogs": "devlogs",
    }

    for folder_name, key in doc_folders.items():
        folder_path = doc_path / folder_name
        if not folder_path.exists() or not folder_path.is_dir():
            continue
        files = []
        for file_path in folder_path.rglob("*"):
            if file_path.is_file():
                files.append(str(file_path.relative_to(folder_path)))
        if files:
            result["existingDocs"][key] = sorted(files)

    tracking_files = sorted((doc_path / "DevLogs").glob("v*_执行跟踪.md"))
    if tracking_files:
        result["existingFeatureList"] = str(tracking_files[-1])

    if is_incremental_project(doc_path):
        result["mode"] = "brownfield"

    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="检测项目模式")
    parser.add_argument("--workspace", type=str, default=".", help="工作空间路径（默认: 当前目录）")
    args = parser.parse_args()

    result = detect_project_mode(args.workspace)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result["mode"] == "greenfield":
        print("\n✅ 检测到 Greenfield 模式（从0到1全新项目开发）", file=sys.stderr)
        print("   建议阅读：references/greenfield/", file=sys.stderr)
    else:
        print("\n✅ 检测到 Brownfield 模式（基于已有系统的迭代优化）", file=sys.stderr)
        print("   建议阅读：references/brownfield/", file=sys.stderr)
        print(f"   现有文档：{len(result['existingDocs'])} 个目录", file=sys.stderr)


if __name__ == "__main__":
    main()
