#!/usr/bin/env python3
"""
文档行数检查工具
用于检查文档是否超过行数限制，并提供拆分建议

使用方法:
    python3 check_doc_size.py --doc-path doc/ [--warn 400] [--max 500]
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import argparse


def count_file_lines(file_path: Path) -> int:
    """统计文件行数"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except Exception as e:
        print(f"⚠️ 无法读取文件 {file_path}: {e}", file=sys.stderr)
        return 0


def suggest_split_strategy(file_path: Path, lines: int) -> dict:
    """
    根据文件类型和行数，提供拆分策略建议
    
    Args:
        file_path: 文件路径
        lines: 文件行数
        
    Returns:
        拆分策略字典 {"num_files": int, "strategy": str, "prefix": str}
    """
    file_name = file_path.stem
    
    # 提取文件编号（如 "1_产品概述" -> "1"）
    if '_' in file_name:
        prefix = file_name.split('_')[0]
    else:
        prefix = "1"
    
    # 根据文件名判断类型和拆分策略
    if "产品概述" in file_name or "概述" in file_name:
        return {
            "num_files": 4,
            "strategy": "按主题拆分（如：核心价值、目标用户、竞品分析、核心功能）",
            "prefix": prefix
        }
    elif "用户画像" in file_name or "用户" in file_name:
        return {
            "num_files": 3,
            "strategy": "按用户维度拆分（如：用户群体、使用场景、用户需求）",
            "prefix": prefix
        }
    elif "核心流程" in file_name or "流程" in file_name:
        return {
            "num_files": 3,
            "strategy": "按流程阶段拆分（如：注册登录、核心业务、异常处理）",
            "prefix": prefix
        }
    elif "系统架构" in file_name or "架构" in file_name:
        return {
            "num_files": 4,
            "strategy": "按架构层次拆分（如：分层架构、模块划分、技术选型、部署架构）",
            "prefix": prefix
        }
    elif "数据表" in file_name or "database" in file_name.lower():
        return {
            "num_files": 3,
            "strategy": "按业务域拆分（如：用户域、订单域、商品域）",
            "prefix": prefix
        }
    elif "API" in file_name.upper() or "接口" in file_name:
        return {
            "num_files": 3,
            "strategy": "按业务模块拆分（如：用户模块、订单模块、支付模块）",
            "prefix": prefix
        }
    else:
        # 通用拆分建议：根据行数估算
        num_parts = min((lines // 300) + 1, 5)  # 每 300 行拆分一个文件，最多 5 个
        return {
            "num_files": num_parts,
            "strategy": "按内容主题拆分（读取文件内容后，根据章节/主题命名）",
            "prefix": prefix
        }


def check_doc_size(
    doc_path: str,
    warn_threshold: int = 400,
    max_threshold: int = 500
) -> Dict[str, any]:
    """
    检查文档行数
    
    Args:
        doc_path: 文档根目录
        warn_threshold: 警告阈值
        max_threshold: 最大限制
        
    Returns:
        检查结果字典
    """
    doc_root = Path(doc_path)
    
    if not doc_root.exists():
        return {
            "success": False,
            "error": f"文档目录不存在: {doc_path}"
        }
    
    results = {
        "success": True,
        "total_files": 0,
        "warnings": [],
        "errors": [],
        "ok_files": []
    }
    
    # 遍历所有 Markdown 文件
    for md_file in doc_root.rglob("*.md"):
        # 跳过 README.md 和特殊文件
        if md_file.name in ["README.md", "00_文档规范.md"]:
            continue
        
        lines = count_file_lines(md_file)
        results["total_files"] += 1
        
        relative_path = md_file.relative_to(doc_root)
        
        if lines > max_threshold:
            # 超过最大限制
            split_strategy = suggest_split_strategy(md_file, lines)
            results["errors"].append({
                "file": str(relative_path),
                "lines": lines,
                "threshold": max_threshold,
                "split_strategy": split_strategy
            })
        elif lines > warn_threshold:
            # 接近限制，警告
            results["warnings"].append({
                "file": str(relative_path),
                "lines": lines,
                "threshold": warn_threshold
            })
        else:
            # 正常
            results["ok_files"].append({
                "file": str(relative_path),
                "lines": lines
            })
    
    return results


def print_report(results: Dict[str, any]):
    """打印检查报告"""
    if not results["success"]:
        print(f"❌ {results['error']}")
        return
    
    print(f"\n📊 文档行数检查报告")
    print(f"=" * 60)
    print(f"总文件数: {results['total_files']}")
    print()
    
    # 打印错误（超过限制）
    if results["errors"]:
        print(f"❌ 超过限制 ({len(results['errors'])} 个文件):")
        for error in results["errors"]:
            strategy = error['split_strategy']
            print(f"   {error['file']}: {error['lines']} 行（限制 {error['threshold']} 行）")
            print(f"   💡 建议拆分为 {strategy['num_files']} 个文件")
            print(f"   📋 拆分策略: {strategy['strategy']}")
            parent_dir = Path(error['file']).parent
            file_name_no_ext = Path(error['file']).stem
            sub_dir = parent_dir / file_name_no_ext
            print(f"   📁 目标目录: {sub_dir}/")
            print(f"   📝 命名规则: {strategy['prefix']}.1_xxx.md, {strategy['prefix']}.2_xxx.md, ...")
            print()
    
    # 打印警告（接近限制）
    if results["warnings"]:
        print(f"⚠️  接近限制 ({len(results['warnings'])} 个文件):")
        for warning in results["warnings"]:
            print(f"   {warning['file']}: {warning['lines']} 行（警告阈值 {warning['threshold']} 行）")
        print()
    
    # 打印正常文件（简洁模式）
    if results["ok_files"]:
        print(f"✅ 正常 ({len(results['ok_files'])} 个文件)")
        # 只显示前 5 个
        for ok in results["ok_files"][:5]:
            print(f"   {ok['file']}: {ok['lines']} 行")
        if len(results["ok_files"]) > 5:
            print(f"   ... 还有 {len(results['ok_files']) - 5} 个文件")
        print()
    
    # 总结
    print("=" * 60)
    if results["errors"]:
        print("❌ 检查失败：有文件超过行数限制")
        sys.exit(1)
    elif results["warnings"]:
        print("⚠️  检查通过：有文件接近限制，建议拆分")
        sys.exit(0)
    else:
        print("✅ 检查通过：所有文件行数正常")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="检查文档行数是否超过限制")
    parser.add_argument(
        "--doc-path",
        required=True,
        help="文档根目录路径"
    )
    parser.add_argument(
        "--warn",
        type=int,
        default=400,
        help="警告阈值（默认 400 行）"
    )
    parser.add_argument(
        "--max",
        type=int,
        default=500,
        help="最大限制（默认 500 行）"
    )
    
    args = parser.parse_args()
    
    results = check_doc_size(
        args.doc_path,
        warn_threshold=args.warn,
        max_threshold=args.max
    )
    
    print_report(results)


if __name__ == "__main__":
    main()
