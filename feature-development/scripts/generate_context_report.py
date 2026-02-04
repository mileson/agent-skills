#!/usr/bin/env python3
"""
生成现有系统上下文报告
用于 Brownfield 模式：生成人类可读的系统现状报告

使用方法:
    python3 generate_context_report.py --doc-path doc/ --output context_report.md
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List


def load_feature_list(feature_list_path: Path) -> Dict:
    """加载 feature_list.json"""
    try:
        with open(feature_list_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}


def scan_code_todos(code_path: Path, max_todos: int = 10) -> List[str]:
    """扫描代码中的 TODO 注释"""
    todos = []
    try:
        for file in code_path.rglob("*.py"):
            if "venv" in str(file) or ".git" in str(file):
                continue
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if "TODO" in line.upper():
                            todo = line.strip().lstrip('#').strip()
                            todos.append(f"{todo} (in {file.name}:{line_num})")
                            if len(todos) >= max_todos:
                                return todos
            except:
                continue
    except:
        pass
    return todos


def generate_context_report(doc_path: str, project_name: str = None) -> str:
    """
    生成现有系统上下文报告
    
    参数:
        doc_path: 文档目录路径
        project_name: 项目名称（可选）
    
    返回:
        Markdown 格式的报告
    """
    doc = Path(doc_path)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = []
    report.append(f"# 现有系统上下文报告\n")
    report.append(f"**生成时间**: {timestamp}\n")
    
    # 1. 项目基本信息
    feature_list_path = doc / "06_dev-logs" / "feature_list.json"
    if feature_list_path.exists():
        feature_list = load_feature_list(feature_list_path)
        project_name = project_name or feature_list.get("project", {}).get("name", "未知项目")
        current_version = feature_list.get("project", {}).get("version", "N/A")
        report.append(f"**项目名称**: {project_name}\n")
        report.append(f"**当前版本**: {current_version}\n\n")
    else:
        report.append(f"**项目名称**: {project_name or '未知项目'}\n")
        report.append(f"**当前版本**: N/A\n\n")
    
    # 2. 产品定位（基于 PRD）
    prd_path = doc / "01_PRD" / "1_产品概述.md"
    if prd_path.exists():
        report.append("## 产品定位（基于 01_PRD/1_产品概述.md）\n\n")
        try:
            with open(prd_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:20]  # 读取前20行
                for line in lines:
                    if "核心价值" in line or "目标用户" in line or "主要功能" in line:
                        report.append(f"- {line.strip()}\n")
        except:
            report.append("- （无法读取）\n")
        report.append("\n")
    
    # 3. 技术架构（基于架构文档）
    arch_path = doc / "02_arch"
    if arch_path.exists():
        report.append("## 技术架构（基于 02_arch/）\n\n")
        
        # 技术选型
        tech_file = arch_path / "1_技术选型.md"
        if tech_file.exists():
            try:
                with open(tech_file, 'r', encoding='utf-8') as f:
                    content = f.read(2000)
                    if "前端" in content:
                        report.append("- 前端技术栈：[已定义，详见文档]\n")
                    if "后端" in content:
                        report.append("- 后端技术栈：[已定义，详见文档]\n")
                    if "部署" in content or "云平台" in content:
                        report.append("- 部署平台：[已定义，详见文档]\n")
            except:
                pass
        report.append("\n")
    
    # 4. 数据库现状（基于数据库设计）
    db_path = doc / "03_database"
    if db_path.exists():
        report.append("## 数据库现状（基于 03_database/）\n\n")
        
        design_file = db_path / "1_数据表设计.md"
        if design_file.exists():
            try:
                with open(design_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    import re
                    tables = re.findall(r'####?\s*表名[：:]\s*`?([a-zA-Z_][a-zA-Z0-9_]*)`?', content)
                    report.append(f"- 现有数据表：{len(tables)} 个\n")
                    if tables:
                        report.append(f"- 核心实体：{', '.join(tables[:5])}\n")
            except:
                report.append("- （无法读取）\n")
        report.append("\n")
    
    # 5. API 现状（基于 API 设计）
    api_path = doc / "04_api"
    if api_path.exists():
        report.append("## API 现状（基于 04_api/）\n\n")
        
        api_file = api_path / "1_RESTful_API.md"
        if api_file.exists():
            try:
                with open(api_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    import re
                    endpoints = re.findall(r'####?\s*(GET|POST|PUT|DELETE)', content, re.IGNORECASE)
                    report.append(f"- 现有端点：{len(endpoints)} 个\n")
                    report.append(f"- 认证方式：[详见文档]\n")
            except:
                report.append("- （无法读取）\n")
        report.append("\n")
    
    # 6. 功能现状（基于 feature_list.json）
    if feature_list_path.exists():
        report.append("## 功能现状（基于 06_dev-logs/feature_list.json）\n\n")
        feature_list = load_feature_list(feature_list_path)
        metadata = feature_list.get("metadata", {})
        
        total = metadata.get("totalFeatures", 0)
        completed = metadata.get("completedFeatures", 0)
        progress = metadata.get("progressPercentage", 0)
        current_version = feature_list.get("project", {}).get("version", "N/A")
        
        report.append(f"- 总功能数：{total} 个\n")
        report.append(f"- 已完成：{completed} 个 ({progress:.1f}%)\n")
        report.append(f"- 当前版本：{current_version}\n")
        
        # 当前 Phase
        phases = feature_list.get("phases", [])
        if phases:
            last_phase = phases[-1]
            report.append(f"- 当前 Phase：{last_phase.get('phaseName', 'N/A')}\n")
        report.append("\n")
    
    # 7. 技术债务和优化空间
    report.append("## 技术债务和优化空间\n\n")
    todos = scan_code_todos(doc.parent)  # 扫描项目根目录
    if todos:
        for todo in todos:
            report.append(f"- [ ] {todo}\n")
    else:
        report.append("- （未发现 TODO 注释）\n")
    
    return ''.join(report)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="生成现有系统上下文报告")
    parser.add_argument("--doc-path", required=True, help="文档目录路径")
    parser.add_argument("--project-name", help="项目名称（可选）")
    parser.add_argument("--output", help="输出 Markdown 文件路径（可选）")
    
    args = parser.parse_args()
    
    # 生成报告
    report = generate_context_report(args.doc_path, args.project_name)
    
    # 输出结果
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ 报告已生成：{output_path}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
