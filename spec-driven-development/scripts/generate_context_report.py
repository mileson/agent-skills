#!/usr/bin/env python3
"""
生成现有系统上下文报告
用于 Brownfield 模式：生成人类可读的系统现状报告

使用方法:
    python3 generate_context_report.py --doc-path Documentation/ --output context_report.md
"""

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from read_existing_docs import read_existing_docs

def extract_metadata_value(label: str, content: str) -> str:
    match = re.search(rf"\*\*{re.escape(label)}\*\*[：:]\s*(.+)", content)
    return match.group(1).strip() if match else ""


def infer_project_name(doc: Path) -> str:
    standard_doc = doc / "00_文档规范.md"
    if standard_doc.exists():
        try:
            content = standard_doc.read_text(encoding="utf-8")
            value = extract_metadata_value("项目名称", content)
            if value:
                return value
        except OSError:
            pass
    return "未知项目"


def load_latest_execution_tracking(devlogs_path: Path) -> Dict:
    tracking_files = sorted(devlogs_path.glob("v*_执行跟踪.md"))
    if not tracking_files:
        return {}

    latest = tracking_files[-1]
    try:
        content = latest.read_text(encoding="utf-8")
    except OSError:
        return {}

    completed = len(re.findall(r"^- \[x\]", content, flags=re.MULTILINE))
    pending = len(re.findall(r"^- \[ \]", content, flags=re.MULTILINE))
    version_match = re.match(r"(v[\d.]+)_执行跟踪\.md", latest.name)
    return {
        "file": latest.name,
        "version": version_match.group(1) if version_match else "N/A",
        "completed": completed,
        "pending": pending,
        "preview": "\n".join(content.splitlines()[:40]),
    }


def scan_code_todos(code_path: Path, max_todos: int = 10) -> List[str]:
    todos = []
    for file_path in code_path.rglob("*.py"):
        if "venv" in str(file_path) or ".git" in str(file_path):
            continue
        try:
            for line_num, line in enumerate(file_path.read_text(encoding="utf-8").splitlines(), start=1):
                if "TODO" in line.upper():
                    todos.append(f"{line.strip().lstrip('#').strip()} (in {file_path.name}:{line_num})")
                    if len(todos) >= max_todos:
                        return todos
        except OSError:
            continue
    return todos


def format_compact_list(items: List[str], limit: int = 3) -> str:
    filtered = [item.strip() for item in items if item and item.strip()]
    if not filtered:
        return ""
    return "；".join(filtered[:limit])


def generate_context_report(doc_path: str, project_name: str = None) -> str:
    doc = Path(doc_path)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execution_tracking = load_latest_execution_tracking(doc / "DevLogs")
    doc_context = read_existing_docs(str(doc))

    report = [
        "# 现有系统上下文报告\n",
        f"**生成时间**：{timestamp}\n",
    ]

    resolved_project_name = project_name or infer_project_name(doc)
    current_version = execution_tracking.get("version", "N/A")
    report.append(f"**项目名称**：{resolved_project_name}\n")
    report.append(f"**当前版本**：{current_version}\n\n")

    prd_path = doc / "Basic/PRD/1_产品概述.md"
    if prd_path.exists():
        report.append("## 产品定位（基于 Basic/PRD/1_产品概述.md）\n\n")
        for line in prd_path.read_text(encoding="utf-8").splitlines()[:30]:
            if "核心价值" in line or "目标用户" in line or "项目背景" in line:
                report.append(f"- {line.strip()}\n")
        report.append("\n")

    arch_path = doc / "Basic/Architecture"
    if arch_path.exists():
        report.append("## 技术架构（基于 Basic/Architecture/）\n\n")
        tech_file = arch_path / "1_技术选型.md"
        if tech_file.exists():
            content = tech_file.read_text(encoding="utf-8")
            if "前端" in content:
                report.append("- 前端技术栈：[已定义，详见技术选型文档]\n")
            if "后端" in content:
                report.append("- 后端技术栈：[已定义，详见技术选型文档]\n")
            if "部署" in content:
                report.append("- 部署平台：[已定义，详见技术选型文档]\n")
        report.append("\n")

    framework_path = doc / "Framework"
    if framework_path.exists():
        framework_context = doc_context.get("framework", {})
        report.append("## Framework 现状\n\n")
        labels = {
            "standards": "Standards",
            "common_capabilities": "CommonCapabilities",
            "problem_solutions": "ProblemSolutions",
        }
        has_framework = False
        for key, label in labels.items():
            docs_in_group = framework_context.get(key, {})
            if not docs_in_group:
                continue
            has_framework = True
            report.append(f"### {label}\n\n")
            for name in sorted(docs_in_group.keys()):
                doc_item = docs_in_group[name]
                template_suffix = "（模板）" if doc_item.get("is_template") else ""
                report.append(f"- {name}{template_suffix}\n")
                if key == "common_capabilities":
                    if doc_item.get("core_function"):
                        report.append(f"  - 核心功能：{doc_item['core_function']}\n")
                    if doc_item.get("position"):
                        report.append(f"  - 定位：{doc_item['position']}\n")
                    scenarios = format_compact_list(doc_item.get("applicable_scenarios", []), limit=3)
                    if scenarios:
                        report.append(f"  - 适用场景：{scenarios}\n")
                    dependencies = format_compact_list(doc_item.get("dependencies", []), limit=3)
                    if dependencies:
                        report.append(f"  - 依赖：{dependencies}\n")
                    dependents = format_compact_list(doc_item.get("dependents", []), limit=3)
                    if dependents:
                        report.append(f"  - 被依赖：{dependents}\n")
                    constraints = format_compact_list(doc_item.get("constraints", []), limit=3)
                    if constraints:
                        report.append(f"  - 约束摘要：{constraints}\n")
                    anti_patterns = format_compact_list(doc_item.get("anti_patterns", []), limit=2)
                    if anti_patterns:
                        report.append(f"  - 反模式：{anti_patterns}\n")
                    if doc_item.get("summary"):
                        report.append(f"  - 摘要：{doc_item['summary']}\n")
                if key == "problem_solutions":
                    scope = format_compact_list(doc_item.get("scope", []), limit=4)
                    if scope:
                        report.append(f"  - 适用范围：{scope}\n")
                    anti_patterns = format_compact_list(doc_item.get("anti_patterns", []), limit=3)
                    if anti_patterns:
                        report.append(f"  - 反模式：{anti_patterns}\n")
                    constraints = format_compact_list(doc_item.get("implementation_constraints", []), limit=3)
                    if constraints:
                        report.append(f"  - 约束摘要：{constraints}\n")
                    verification = format_compact_list(doc_item.get("verification", []), limit=2)
                    if verification:
                        report.append(f"  - 验证方式：{verification}\n")
                    if doc_item.get("summary"):
                        report.append(f"  - 摘要：{doc_item['summary']}\n")
            report.append("\n")
        if not has_framework:
            report.append("- （暂无 Framework 文档）\n\n")

        problem_solution_docs = framework_context.get("problem_solutions", {})
        if problem_solution_docs:
            report.append("### Agent 读取建议（ProblemSolutions）\n\n")
            for name, doc_item in sorted(problem_solution_docs.items()):
                if doc_item.get("is_template"):
                    continue
                scope = format_compact_list(doc_item.get("scope", []), limit=3) or "未标注"
                constraints = format_compact_list(doc_item.get("implementation_constraints", []), limit=2) or "需查看原文"
                report.append(f"- `{name}`：适用范围 {scope}；优先检查 {constraints}\n")
            report.append("\n")

        capability_docs = framework_context.get("common_capabilities", {})
        if capability_docs:
            report.append("### Agent 读取建议（CommonCapabilities）\n\n")
            for name, doc_item in sorted(capability_docs.items()):
                if doc_item.get("is_template"):
                    continue
                scenarios = format_compact_list(doc_item.get("applicable_scenarios", []), limit=3) or "未标注"
                constraints = format_compact_list(doc_item.get("constraints", []), limit=2) or "需查看原文"
                report.append(f"- `{name}`：适用场景 {scenarios}；优先遵守 {constraints}\n")
            report.append("\n")

    modules_root = doc / "Modules"
    if modules_root.exists():
        report.append("## 模块文档现状\n\n")
        module_context = doc_context.get("modules", {})
        if module_context:
            for relative_path, module in module_context.items():
                report.append(
                    f"- `{relative_path}`：{module.get('version', 'N/A')}，最近更新 {module.get('updated_at', 'N/A')} / {module.get('updated_by', 'N/A')}\n"
                )
                if module.get("core_function") and module["core_function"] != "N/A":
                    report.append(f"  - 核心功能：{module['core_function']}\n")
                if module.get("position"):
                    report.append(f"  - 定位：{module['position']}\n")
                if module.get("dependencies"):
                    report.append(f"  - 依赖：{', '.join(module['dependencies'][:4])}\n")
                if module.get("dependents"):
                    report.append(f"  - 被依赖：{', '.join(module['dependents'][:4])}\n")
                if module.get("related_docs"):
                    report.append(f"  - 相关文档：{', '.join(module['related_docs'][:3])}\n")
                if module.get("related_modules"):
                    report.append(f"  - 关联模块：{', '.join(module['related_modules'][:4])}\n")
        else:
            report.append("- 当前仅存在模块模板，尚未沉淀具体模块主文档\n")
        report.append("\n")

    db_path = doc / "Basic/Database/1_数据表设计.md"
    if db_path.exists():
        report.append("## 数据库现状（基于 Basic/Database/）\n\n")
        content = db_path.read_text(encoding="utf-8")
        import re
        tables = re.findall(r"####?\s*表名[：:]\s*`?([a-zA-Z_][a-zA-Z0-9_]*)`?", content)
        report.append(f"- 现有数据表：{len(tables)} 个\n")
        if tables:
            report.append(f"- 核心实体：{', '.join(tables[:5])}\n")
        report.append("\n")

    api_path = doc / "Basic/API/1_RESTful_API.md"
    if api_path.exists():
        report.append("## API 现状（基于 Basic/API/1_RESTful_API.md）\n\n")
        content = api_path.read_text(encoding="utf-8")
        import re
        endpoints = re.findall(r"####?\s*(GET|POST|PUT|DELETE|PATCH)", content, re.IGNORECASE)
        report.append(f"- 现有端点：{len(endpoints)} 个\n")
        report.append("- 认证方式：[详见 API 文档]\n\n")

    if execution_tracking:
        report.append("## 执行现状（基于 DevLogs/v*_执行跟踪.md）\n\n")
        report.append(f"- 当前执行跟踪文件：{execution_tracking.get('file', 'N/A')}\n")
        report.append(f"- 当前版本：{execution_tracking.get('version', 'N/A')}\n")
        report.append(f"- 已完成任务：{execution_tracking.get('completed', 0)} 个\n")
        report.append(f"- 待完成任务：{execution_tracking.get('pending', 0)} 个\n\n")

    report.append("## 技术债务和优化空间\n\n")
    todos = scan_code_todos(doc.parent)
    if todos:
        for todo in todos:
            report.append(f"- [ ] {todo}\n")
    else:
        report.append("- （未发现 TODO 注释）\n")

    return "".join(report)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="生成现有系统上下文报告")
    parser.add_argument("--doc-path", required=True, help="文档目录路径")
    parser.add_argument("--project-name", help="项目名称（可选）")
    parser.add_argument("--output", help="输出 Markdown 文件路径（可选）")
    args = parser.parse_args()

    report = generate_context_report(args.doc_path, args.project_name)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"✅ 报告已生成：{output_path}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
