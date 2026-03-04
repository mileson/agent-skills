#!/usr/bin/env python3
"""
智能读取现有文档脚本
用于 Brownfield 模式：避免全量加载，只读取关键信息

使用方法:
    python3 read_existing_docs.py --doc-path Documentation/ [--output context.json]
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List


def is_folder_manual_file(path: Path) -> bool:
    """判断是否为文件夹说明书。"""
    return path.name == "README.md" or path.name.endswith("_README.md")


def extract_first_header(md_file: Path) -> str:
    """提取 Markdown 文件的第一个标题。"""
    try:
        for line in md_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("#"):
                return line.strip("#").strip()
    except OSError:
        pass
    return md_file.stem


def extract_table_names(db_design_file: Path, max_lines: int = 500) -> List[str]:
    """从数据库设计文档中提取表名。"""
    try:
        content = "\n".join(db_design_file.read_text(encoding="utf-8").splitlines()[:max_lines])
    except OSError:
        return []

    tables = []
    tables.extend(re.findall(r"####?\s*表名[：:]\s*`?([a-zA-Z_][a-zA-Z0-9_]*)`?", content))
    tables.extend(re.findall(r'CREATE\s+TABLE\s+["`]?([a-zA-Z_][a-zA-Z0-9_]*)["`]?', content, re.IGNORECASE))
    return sorted(set(tables))


def extract_api_endpoints(api_file: Path, max_lines: int = 500) -> List[Dict]:
    """从 API 文档中提取接口端点。"""
    try:
        content = "\n".join(api_file.read_text(encoding="utf-8").splitlines()[:max_lines])
    except OSError:
        return []

    matches = re.findall(r"####?\s*(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s\n]*)", content, re.IGNORECASE)
    return [{"method": method.upper(), "path": path} for method, path in matches]


def extract_list_items(section_title: str, content: str) -> List[str]:
    """提取指定章节下的列表项。"""
    pattern = rf"{re.escape(section_title)}\n((?:\n|.+)+?)(?:\n### |\n## |\Z)"
    match = re.search(pattern, content)
    if not match:
        return []
    section = match.group(1)
    return [line.strip("- ").strip() for line in section.splitlines() if line.strip().startswith("-")]


def extract_section_text(section_title: str, content: str) -> str:
    """提取指定章节下的正文文本。"""
    pattern = rf"{re.escape(section_title)}\n((?:\n|.+)+?)(?:\n### |\n## |\Z)"
    match = re.search(pattern, content)
    if not match:
        return ""
    lines = [line.strip() for line in match.group(1).splitlines() if line.strip()]
    return " ".join(lines[:3])


def extract_metadata_value(label: str, content: str) -> str:
    """提取头部元信息字段。"""
    match = re.search(rf"\*\*{re.escape(label)}\*\*[：:]\s*(.+)", content)
    return match.group(1).strip() if match else "N/A"


def extract_section_lines(section_title: str, content: str, max_items: int = 10) -> List[str]:
    """提取指定章节下的非空文本行，兼容列表和普通文本。"""
    pattern = rf"{re.escape(section_title)}\n((?:\n|.+)+?)(?:\n### |\n## |\Z)"
    match = re.search(pattern, content)
    if not match:
        return []
    lines = []
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r"^[-*]\s*", "", line)
        lines.append(line)
        if len(lines) >= max_items:
            break
    return lines


def extract_first_matching_section_text(candidates: List[str], content: str) -> str:
    """按候选标题顺序提取正文文本。"""
    for title in candidates:
        text = extract_section_text(title, content)
        if text:
            return text
    return ""


def extract_first_matching_section_lines(candidates: List[str], content: str, max_items: int = 10) -> List[str]:
    """按候选标题顺序提取列表或文本行。"""
    for title in candidates:
        items = extract_list_items(title, content)
        if items:
            return items[:max_items]
        lines = extract_section_lines(title, content, max_items=max_items)
        if lines:
            return lines[:max_items]
    return []


def extract_problem_solution_scope(content: str) -> List[str]:
    """提取问题方案适用范围。"""
    metadata_scope = extract_metadata_value("适用范围", content)
    if metadata_scope != "N/A":
        return [item.strip() for item in re.split(r"[、,，/]", metadata_scope) if item.strip()]

    task_types = extract_list_items("### 关联任务类型 (Related Task Types)", content)
    if task_types:
        return task_types[:10]

    boundary_lines = extract_section_lines("### 适用边界 (Boundaries)", content, max_items=3)
    if boundary_lines:
        return boundary_lines

    return []


def build_problem_solution_summary(content: str) -> str:
    """构造问题方案摘要，优先突出标准解法和约束。"""
    standard_solution = extract_section_text("### 标准解决方案 (Standard Solution)", content)
    constraints = extract_section_lines("### 实施约束 (Implementation Constraints)", content, max_items=2)
    anti_patterns = extract_list_items("### 错误做法 / 反模式 (Anti-Patterns)", content)[:2]

    parts = []
    if standard_solution:
        parts.append(f"解法：{standard_solution}")
    if constraints:
        parts.append(f"约束：{'；'.join(constraints)}")
    if anti_patterns:
        parts.append(f"反模式：{'；'.join(anti_patterns)}")
    return " | ".join(parts)


def build_capability_summary(content: str) -> str:
    """构造通用能力摘要，优先突出定位、约束和最佳实践。"""
    core_function = extract_section_text("### 核心功能 (Core Function)", content)
    scenarios = extract_first_matching_section_lines(
        ["## 1. 适用场景", "## 适用场景", "### 适用场景"],
        content,
        max_items=2,
    )
    constraints = extract_first_matching_section_lines(
        ["## 4. 状态与约束", "## 状态与约束", "### 状态与约束"],
        content,
        max_items=2,
    )
    best_practices = extract_first_matching_section_lines(
        ["## 7. 最佳实践", "## 最佳实践", "### 最佳实践"],
        content,
        max_items=2,
    )

    parts = []
    if core_function:
        parts.append(f"能力：{core_function}")
    if scenarios:
        parts.append(f"适用场景：{'；'.join(scenarios)}")
    if constraints:
        parts.append(f"约束：{'；'.join(constraints)}")
    if best_practices:
        parts.append(f"最佳实践：{'；'.join(best_practices)}")
    return " | ".join(parts)


def read_existing_docs(doc_path: str, max_lines_per_file: int = 500) -> Dict:
    """读取新结构下的关键信息。"""
    doc = Path(doc_path)
    result = {
        "basic": {"prd": {}, "architecture": {}, "database": {}, "api": {}, "ui": {}, "testing": {}},
        "framework": {"standards": {}, "common_capabilities": {}, "problem_solutions": {}},
        "modules": {},
        "summary": "",
    }

    prd_path = doc / "Basic/PRD"
    for file_name in ("1_产品概述.md", "3_核心流程.md"):
        file_path = prd_path / file_name
        if not file_path.exists():
            continue
        lines = file_path.read_text(encoding="utf-8").splitlines()[:max_lines_per_file]
        result["basic"]["prd"][file_name] = {
            "title": extract_first_header(file_path),
            "preview": "\n".join(lines[:12]),
            "line_count": len(lines),
        }

    arch_path = doc / "Basic/Architecture"
    for file_path in arch_path.glob("*.md"):
        lines = file_path.read_text(encoding="utf-8").splitlines()
        result["basic"]["architecture"][file_path.name] = {
            "title": extract_first_header(file_path),
            "preview": "\n".join(lines[:min(40, len(lines))]),
            "line_count": len(lines),
            "truncated": len(lines) > max_lines_per_file,
        }

    db_design = doc / "Basic/Database/1_数据表设计.md"
    if db_design.exists():
        tables = extract_table_names(db_design)
        result["basic"]["database"] = {
            "table_count": len(tables),
            "tables": tables[:20],
            "core_entities": tables[:5],
        }

    api_doc = doc / "Basic/API/1_RESTful_API.md"
    if api_doc.exists():
        endpoints = extract_api_endpoints(api_doc)
        result["basic"]["api"] = {
            "endpoint_count": len(endpoints),
            "endpoints": endpoints[:20],
            "methods": sorted({item["method"] for item in endpoints}),
        }

    ui_doc = doc / "Basic/UI/1_信息架构总览.md"
    if ui_doc.exists():
        lines = ui_doc.read_text(encoding="utf-8").splitlines()[:max_lines_per_file]
        result["basic"]["ui"]["1_信息架构总览.md"] = {
            "title": extract_first_header(ui_doc),
            "preview": "\n".join(lines[:25]),
            "line_count": len(lines),
        }

    testing_doc = doc / "Basic/Testing/1_测试策略.md"
    if testing_doc.exists():
        lines = testing_doc.read_text(encoding="utf-8").splitlines()[:max_lines_per_file]
        result["basic"]["testing"]["1_测试策略.md"] = {
            "title": extract_first_header(testing_doc),
            "preview": "\n".join(lines[:20]),
            "line_count": len(lines),
        }

    framework_path = doc / "Framework"
    framework_map = {
        "Standards": "standards",
        "CommonCapabilities": "common_capabilities",
        "ProblemSolutions": "problem_solutions",
    }
    for folder_name, bucket in framework_map.items():
        folder_path = framework_path / folder_name
        if not folder_path.exists():
            continue
        for file_path in folder_path.glob("*.md"):
            if is_folder_manual_file(file_path):
                continue
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            entry = {
                "title": extract_first_header(file_path),
                "preview": "\n".join(lines[:min(30, len(lines))]),
                "line_count": len(lines),
                "version": extract_metadata_value("文档版本", content),
                "updated_at": extract_metadata_value("更新日期", content),
                "updated_by": extract_metadata_value("更新人", content),
                "is_template": "模板" in file_path.stem or "_template" in file_path.stem.lower(),
            }

            if bucket == "common_capabilities":
                entry.update(
                    {
                        "core_function": extract_section_text("### 核心功能 (Core Function)", content),
                        "position": extract_section_text("### 定位 (Position)", content),
                        "inputs": extract_list_items("### 输入 (Input)", content)[:10],
                        "outputs": extract_list_items("### 输出 (Output)", content)[:10],
                        "dependencies": extract_list_items("### 依赖 (Dependency)", content)[:10],
                        "dependents": extract_list_items("### 被依赖 (Dependents)", content)[:10],
                        "applicable_scenarios": extract_first_matching_section_lines(
                            ["## 1. 适用场景", "## 适用场景", "### 适用场景"],
                            content,
                        ),
                        "design_goals": extract_first_matching_section_lines(
                            ["## 2. 设计目标", "## 设计目标", "### 设计目标"],
                            content,
                        ),
                        "contracts": extract_first_matching_section_lines(
                            ["## 3. 输入输出与 Contract", "## 输入输出与 Contract", "### 输入输出与 Contract"],
                            content,
                        ),
                        "constraints": extract_first_matching_section_lines(
                            ["## 4. 状态与约束", "## 状态与约束", "### 状态与约束"],
                            content,
                        ),
                        "best_practices": extract_first_matching_section_lines(
                            ["## 7. 最佳实践", "## 最佳实践", "### 最佳实践"],
                            content,
                        ),
                        "anti_patterns": extract_first_matching_section_lines(
                            ["## 8. 反模式", "## 反模式", "### 反模式"],
                            content,
                        ),
                        "usage_examples": extract_first_matching_section_lines(
                            ["## 9. 使用示例", "## 使用示例", "### 使用示例"],
                            content,
                        ),
                        "summary": build_capability_summary(content),
                    }
                )

            if bucket == "problem_solutions":
                entry.update(
                    {
                        "scope": extract_problem_solution_scope(content),
                        "background": extract_section_text("### 问题背景 (Background)", content),
                        "trigger_scenarios": extract_list_items("### 触发场景 (Trigger Scenarios)", content)[:10],
                        "symptoms": extract_list_items("### 问题表现 (Symptoms)", content)[:10],
                        "anti_patterns": extract_list_items("### 错误做法 / 反模式 (Anti-Patterns)", content)[:10],
                        "standard_solution": extract_section_text("### 标准解决方案 (Standard Solution)", content),
                        "implementation_constraints": extract_list_items("### 实施约束 (Implementation Constraints)", content)[:10],
                        "verification": extract_list_items("### 验证方式 (Verification)", content)[:10],
                        "boundaries": extract_section_lines("### 适用边界 (Boundaries)", content)[:10],
                        "related_docs": extract_list_items("### 相关文档 (Related Docs)", content)[:10],
                        "related_task_types": extract_list_items("### 关联任务类型 (Related Task Types)", content)[:10],
                        "summary": build_problem_solution_summary(content),
                    }
                )

            result["framework"][bucket][file_path.name] = entry

    modules_root = doc / "Modules"
    for file_path in modules_root.rglob("*.md"):
        if is_folder_manual_file(file_path):
            continue
        if "_template" in file_path.parts:
            continue
        content = file_path.read_text(encoding="utf-8")
        result["modules"][str(file_path.relative_to(modules_root))] = {
            "title": extract_first_header(file_path),
            "project": extract_metadata_value("项目名称", content),
            "system": extract_metadata_value("所属系统", content),
            "version": extract_metadata_value("文档版本", content),
            "updated_at": extract_metadata_value("更新日期", content),
            "updated_by": extract_metadata_value("更新人", content),
            "core_function": extract_section_text("### 核心功能 (Core Function)", content),
            "position": extract_section_text("### 定位 (Position)", content),
            "inputs": extract_list_items("### 输入 (Input)", content)[:10],
            "outputs": extract_list_items("### 输出 (Output)", content)[:10],
            "dependencies": extract_list_items("### 依赖 (Dependency)", content)[:10],
            "dependents": extract_list_items("### 被依赖 (Dependents)", content)[:10],
            "related_docs": extract_list_items("### 相关文档 (Related Docs)", content)[:10],
            "related_modules": extract_list_items("### 关联模块 (Related Modules)", content)[:10],
        }

    summary_parts = []
    basic_count = sum(len(section) if isinstance(section, dict) else 0 for section in result["basic"].values())
    if basic_count:
        summary_parts.append(f"基础文档: {basic_count} 个入口")
    framework_total = sum(len(group) for group in result["framework"].values())
    if framework_total:
        summary_parts.append(f"Framework: {framework_total} 个文档")
    problem_solution_total = len(result["framework"]["problem_solutions"])
    if problem_solution_total:
        summary_parts.append(f"问题方案: {problem_solution_total} 个")
    capability_total = len(result["framework"]["common_capabilities"])
    if capability_total:
        summary_parts.append(f"通用能力: {capability_total} 个")
    if result["modules"]:
        summary_parts.append(f"模块文档: {len(result['modules'])} 个")
    if result["basic"]["database"].get("table_count"):
        summary_parts.append(f"数据库: {result['basic']['database']['table_count']} 个表")
    if result["basic"]["api"].get("endpoint_count"):
        summary_parts.append(f"API: {result['basic']['api']['endpoint_count']} 个端点")

    result["summary"] = ", ".join(summary_parts) if summary_parts else "无文档"
    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="智能读取现有文档")
    parser.add_argument("--doc-path", required=True, help="文档目录路径")
    parser.add_argument("--max-lines", type=int, default=500, help="每个文件最多读取行数")
    parser.add_argument("--output", help="输出 JSON 文件路径（可选）")
    args = parser.parse_args()

    result = read_existing_docs(args.doc_path, args.max_lines)
    output = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"✅ 结果已保存到：{args.output}", file=sys.stderr)
    else:
        print(output)

    print(f"\n📊 摘要：{result['summary']}", file=sys.stderr)


if __name__ == "__main__":
    main()
