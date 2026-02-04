#!/usr/bin/env python3
"""
智能读取现有文档脚本
用于 Brownfield 模式：避免全量加载，只读取关键信息

使用方法:
    python3 read_existing_docs.py --doc-path doc/ [--output context.json]
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional


def extract_first_header(md_file: Path) -> str:
    """提取 Markdown 文件的第一个标题"""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#'):
                    return line.strip('#').strip()
        return md_file.stem
    except:
        return md_file.stem


def extract_table_names(db_design_file: Path, max_lines: int = 500) -> List[str]:
    """从数据库设计文档中提取表名"""
    tables = []
    try:
        with open(db_design_file, 'r', encoding='utf-8') as f:
            content = f.read(max_lines * 100)  # 读取前 max_lines 行内容
            # 匹配 Markdown 表格中的表名模式
            # 示例：#### 表名：users
            table_pattern = r'####?\s*表名[：:]\s*`?([a-zA-Z_][a-zA-Z0-9_]*)`?'
            tables = re.findall(table_pattern, content)
            
            # 也匹配 CREATE TABLE 语句
            create_pattern = r'CREATE\s+TABLE\s+["`]?([a-zA-Z_][a-zA-Z0-9_]*)["`]?'
            tables.extend(re.findall(create_pattern, content, re.IGNORECASE))
        
        return list(set(tables))  # 去重
    except:
        return []


def extract_api_endpoints(api_file: Path, max_lines: int = 500) -> List[Dict]:
    """从 API 文档中提取接口端点"""
    endpoints = []
    try:
        with open(api_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:max_lines]
            content = ''.join(lines)
            
            # 匹配接口定义模式
            # 示例：#### GET /users/{id}
            endpoint_pattern = r'####?\s*(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s\n]*)'
            matches = re.findall(endpoint_pattern, content, re.IGNORECASE)
            
            for method, path in matches:
                endpoints.append({
                    "method": method.upper(),
                    "path": path
                })
        
        return endpoints
    except:
        return []


def detect_latest_version(files: List[Path]) -> Optional[Path]:
    """检测最新版本的文档（v2.0 > v1.5 > v1.0）"""
    version_pattern = r'v?(\d+)\.(\d+)'
    latest_file = None
    latest_version = (-1, -1)
    
    for file in files:
        match = re.search(version_pattern, file.name)
        if match:
            major, minor = int(match.group(1)), int(match.group(2))
            if (major, minor) > latest_version:
                latest_version = (major, minor)
                latest_file = file
    
    # 如果没有版本号，返回第一个文件
    return latest_file if latest_file else (files[0] if files else None)


def read_existing_docs(doc_path: str, max_lines_per_file: int = 500) -> Dict:
    """
    智能读取现有文档
    
    参数:
        doc_path: 文档目录路径
        max_lines_per_file: 每个文件最多读取行数
    
    返回:
        {
            "prd": {...},
            "arch": {...},
            "database": {...},
            "api": {...},
            "summary": "..."
        }
    """
    doc = Path(doc_path)
    result = {
        "prd": {},
        "arch": {},
        "database": {},
        "api": {},
        "summary": ""
    }
    
    # 1. 读取 PRD
    prd_path = doc / "01_PRD"
    if prd_path.exists():
        # 只读取核心文档
        core_files = ["1_产品概述.md", "3_核心流程.md"]
        for file_name in core_files:
            file_path = prd_path / file_name
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:max_lines_per_file]
                    result["prd"][file_name] = {
                        "title": extract_first_header(file_path),
                        "preview": ''.join(lines[:10]),  # 前10行预览
                        "line_count": len(lines)
                    }
    
    # 2. 读取架构文档
    arch_path = doc / "02_arch"
    if arch_path.exists():
        for file in arch_path.glob("*.md"):
            with open(file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                preview_lines = min(50, len(lines))
                result["arch"][file.name] = {
                    "title": extract_first_header(file),
                    "preview": ''.join(lines[:preview_lines]),
                    "line_count": len(lines),
                    "truncated": len(lines) > max_lines_per_file
                }
    
    # 3. 读取数据库设计（提取表名）
    db_path = doc / "03_database"
    if db_path.exists():
        design_file = db_path / "1_数据表设计.md"
        if design_file.exists():
            tables = extract_table_names(design_file)
            result["database"] = {
                "table_count": len(tables),
                "tables": tables[:20],  # 最多显示前20个
                "core_entities": tables[:5] if tables else []
            }
    
    # 4. 读取 API 设计（提取端点）
    api_path = doc / "04_api"
    if api_path.exists():
        api_file = api_path / "1_RESTful_API.md"
        if api_file.exists():
            endpoints = extract_api_endpoints(api_file)
            result["api"] = {
                "endpoint_count": len(endpoints),
                "endpoints": endpoints[:20],  # 最多显示前20个
                "methods": list(set(ep["method"] for ep in endpoints))
            }
    
    # 5. 生成摘要
    summary_parts = []
    if result["prd"]:
        summary_parts.append(f"PRD: {len(result['prd'])} 个核心文档")
    if result["arch"]:
        summary_parts.append(f"架构: {len(result['arch'])} 个文档")
    if result["database"].get("table_count"):
        summary_parts.append(f"数据库: {result['database']['table_count']} 个表")
    if result["api"].get("endpoint_count"):
        summary_parts.append(f"API: {result['api']['endpoint_count']} 个端点")
    
    result["summary"] = ", ".join(summary_parts) if summary_parts else "无文档"
    
    return result


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="智能读取现有文档")
    parser.add_argument("--doc-path", required=True, help="文档目录路径")
    parser.add_argument("--max-lines", type=int, default=500, help="每个文件最多读取行数")
    parser.add_argument("--output", help="输出 JSON 文件路径（可选）")
    
    args = parser.parse_args()
    
    # 读取文档
    result = read_existing_docs(args.doc_path, args.max_lines)
    
    # 输出结果
    output_json = json.dumps(result, indent=2, ensure_ascii=False)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"✅ 结果已保存到：{args.output}", file=sys.stderr)
    else:
        print(output_json)
    
    # 输出摘要
    print(f"\n📊 摘要：{result['summary']}", file=sys.stderr)


if __name__ == "__main__":
    main()
