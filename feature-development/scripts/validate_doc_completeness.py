#!/usr/bin/env python3
"""
验证文档完整性脚本
检查文档是否符合规范（借鉴 nn-gene 的质量检查清单）

使用方法:
    python3 validate_doc_completeness.py --doc-path doc/
"""

import os
import sys
from pathlib import Path
from typing import Dict, List


def check_required_directories(doc_path: Path) -> Dict:
    """检查必需的目录是否存在"""
    required_dirs = [
        "01_PRD",
        "02_arch",
        "03_database",
        "04_api",
        "06_dev-logs",
        "07_testing"
    ]
    
    result = {"missing": [], "exists": []}
    
    for dir_name in required_dirs:
        dir_path = doc_path / dir_name
        if dir_path.exists():
            result["exists"].append(dir_name)
        else:
            result["missing"].append(dir_name)
    
    return result


def check_required_files(doc_path: Path) -> Dict:
    """检查必需的文件是否存在"""
    required_files = {
        "00_文档规范.md": doc_path / "00_文档规范.md",
        "feature_list.json": doc_path / "06_dev-logs" / "feature_list.json",
        "PROGRESS.md": doc_path / "06_dev-logs" / "PROGRESS.md"
    }
    
    result = {"missing": [], "exists": []}
    
    for file_name, file_path in required_files.items():
        if file_path.exists():
            result["exists"].append(file_name)
        else:
            result["missing"].append(file_name)
    
    return result


def check_doc_line_counts(doc_path: Path, max_lines: int = 10000) -> Dict:
    """检查文档行数（借鉴 nn-gene 的行数控制）"""
    result = {"violations": [], "warnings": []}
    
    for md_file in doc_path.rglob("*.md"):
        if "README" in md_file.name:
            continue
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                line_count = len(lines)
                
                if line_count > max_lines:
                    result["violations"].append({
                        "file": str(md_file.relative_to(doc_path)),
                        "lines": line_count,
                        "suggestion": f"超过 {max_lines} 行，建议拆分"
                    })
                elif line_count > max_lines * 0.8:
                    result["warnings"].append({
                        "file": str(md_file.relative_to(doc_path)),
                        "lines": line_count,
                        "suggestion": f"接近 {max_lines} 行，考虑拆分"
                    })
        except:
            continue
    
    return result


def check_mermaid_diagrams(doc_path: Path) -> Dict:
    """检查 Mermaid 图表是否包含样式头"""
    result = {"missing_style": [], "has_style": []}
    
    for md_file in doc_path.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 检查是否有 Mermaid 代码块
                if "```mermaid" in content:
                    # 检查是否有样式头
                    if "%%{init:" in content or "classDef" in content:
                        result["has_style"].append(str(md_file.relative_to(doc_path)))
                    else:
                        result["missing_style"].append(str(md_file.relative_to(doc_path)))
        except:
            continue
    
    return result


def validate_doc_completeness(doc_path: str) -> Dict:
    """
    验证文档完整性
    
    参数:
        doc_path: 文档目录路径
    
    返回:
        验证结果
    """
    doc = Path(doc_path)
    
    if not doc.exists():
        return {"error": f"文档目录不存在：{doc_path}"}
    
    result = {
        "directories": check_required_directories(doc),
        "files": check_required_files(doc),
        "line_counts": check_doc_line_counts(doc),
        "mermaid": check_mermaid_diagrams(doc)
    }
    
    return result


def print_validation_report(result: Dict):
    """打印验证报告"""
    print("\n" + "=" * 60)
    print("📋 文档完整性验证报告")
    print("=" * 60)
    
    # 1. 目录检查
    print("\n1️⃣  必需目录检查")
    if result["directories"]["missing"]:
        print(f"   ❌ 缺失 {len(result['directories']['missing'])} 个目录：")
        for dir_name in result["directories"]["missing"]:
            print(f"      - {dir_name}")
    else:
        print(f"   ✅ 所有必需目录已创建 ({len(result['directories']['exists'])} 个)")
    
    # 2. 文件检查
    print("\n2️⃣  必需文件检查")
    if result["files"]["missing"]:
        print(f"   ❌ 缺失 {len(result['files']['missing'])} 个文件：")
        for file_name in result["files"]["missing"]:
            print(f"      - {file_name}")
    else:
        print(f"   ✅ 所有必需文件已创建 ({len(result['files']['exists'])} 个)")
    
    # 3. 行数检查
    print("\n3️⃣  文档行数检查")
    line_result = result["line_counts"]
    if line_result["violations"]:
        print(f"   ❌ {len(line_result['violations'])} 个文档超过行数限制：")
        for violation in line_result["violations"]:
            print(f"      - {violation['file']}: {violation['lines']} 行 - {violation['suggestion']}")
    elif line_result["warnings"]:
        print(f"   ⚠️  {len(line_result['warnings'])} 个文档接近行数限制：")
        for warning in line_result["warnings"]:
            print(f"      - {warning['file']}: {warning['lines']} 行 - {warning['suggestion']}")
    else:
        print(f"   ✅ 所有文档行数符合规范")
    
    # 4. Mermaid 图表检查
    print("\n4️⃣  Mermaid 图表样式检查")
    mermaid_result = result["mermaid"]
    if mermaid_result["missing_style"]:
        print(f"   ⚠️  {len(mermaid_result['missing_style'])} 个文档的 Mermaid 图表缺少样式头：")
        for file in mermaid_result["missing_style"]:
            print(f"      - {file}")
    elif mermaid_result["has_style"]:
        print(f"   ✅ 所有 Mermaid 图表包含样式头 ({len(mermaid_result['has_style'])} 个)")
    else:
        print(f"   ℹ️  未找到 Mermaid 图表")
    
    print("\n" + "=" * 60)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="验证文档完整性")
    parser.add_argument("--doc-path", required=True, help="文档目录路径")
    parser.add_argument("--max-lines", type=int, default=10000, help="最大行数限制")
    
    args = parser.parse_args()
    
    # 验证文档
    result = validate_doc_completeness(args.doc_path)
    
    if "error" in result:
        print(f"❌ {result['error']}", file=sys.stderr)
        sys.exit(1)
    
    # 打印报告
    print_validation_report(result)
    
    # 判断是否通过
    has_errors = (
        result["directories"]["missing"] or 
        result["files"]["missing"] or 
        result["line_counts"]["violations"]
    )
    
    if has_errors:
        print("\n❌ 文档验证失败，请修复上述问题", file=sys.stderr)
        sys.exit(1)
    else:
        print("\n✅ 文档验证通过", file=sys.stderr)


if __name__ == "__main__":
    main()
