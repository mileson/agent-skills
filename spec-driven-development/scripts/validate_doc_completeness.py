#!/usr/bin/env python3
"""
验证文档完整性脚本
检查文档是否符合 Spec-Driven v3 规范

使用方法:
    python3 validate_doc_completeness.py --doc-path Documentation/
"""

import sys
from pathlib import Path
from typing import Dict, List


MODULE_METADATA_FIELDS = [
    "项目名称",
    "所属系统",
    "文档版本",
    "编写日期",
    "更新日期",
    "编写人",
    "更新人",
]

REQUIREMENT_OVERVIEW_FIELDS = [
    "### 模块定位",
    "### 目标用户",
    "### 核心价值",
    "### 触发入口",
    "### 核心场景",
    "### 成功结果",
    "### 成功标准",
]

TECHNICAL_MANUAL_FIELDS = [
    "### 核心功能 (Core Function)",
    "### 输入 (Input)",
    "### 输出 (Output)",
    "### 定位 (Position)",
    "### 依赖 (Dependency)",
    "### 被依赖 (Dependents)",
    "### 相关文档 (Related Docs)",
    "### 关联模块 (Related Modules)",
]

REQUIREMENT_REQUIRED_SECTIONS = [
    "## 模块概览卡",
    "## 1. 业务背景",
    "## 2. 目标用户与产品定位",
    "## 3. 业务场景",
    "## 4. 业务场景流程",
    "## 5. 功能需求",
    "## 6. 业务规则",
    "## 7. 业务 ASCII 交互稿",
    "## 8. 验收标准",
    "## 9. 边界与待确认项",
]

TECHNICAL_REQUIRED_SECTIONS = [
    "## 模块说明书 (Module Manual)",
    "## 1. 需求映射",
    "## 2. 系统架构",
    "## 3. 数据 / 状态模型",
    "## 4. Contract / API / 事件",
    "## 5. 技术流程设计",
    "## 6. 异常与补偿",
    "## 7. 实施现状",
    "## 8. 测试设计",
    "## 9. 风险与待办",
    "## 10. 附录",
    "## 11. FAQ / 常见问题",
    "## 12. 变更检查清单",
    "## 13. 代码同步说明",
]

PROBLEM_SOLUTION_FIELDS = [
    "### 问题背景 (Background)",
    "### 触发场景 (Trigger Scenarios)",
    "### 问题表现 (Symptoms)",
    "### 根因分析 (Root Cause)",
    "### 错误做法 / 反模式 (Anti-Patterns)",
    "### 标准解决方案 (Standard Solution)",
    "### 实施约束 (Implementation Constraints)",
    "### 验证方式 (Verification)",
    "### 适用边界 (Boundaries)",
]

CAPABILITY_FIELDS = [
    "### 核心功能 (Core Function)",
    "### 输入 (Input)",
    "### 输出 (Output)",
    "### 定位 (Position)",
    "### 依赖 (Dependency)",
    "### 被依赖 (Dependents)",
]

OPTIONAL_STRONG_RULES = {
    "faq": {
        "label": "FAQ / 常见问题",
        "patterns": ["FAQ / 常见问题", "常见问题"],
    },
    "checklist": {
        "label": "检查清单",
        "patterns": ["变更检查清单", "检查清单", "验证清单", "关键检查清单"],
    },
    "code_sync": {
        "label": "代码同步说明",
        "patterns": ["代码同步说明", "同步实际代码实现", "基于实际代码实现同步", "基于实际代码审查更新"],
    },
    "implementation_status": {
        "label": "实施现状",
        "patterns": ["## 7. 实施现状"],
        "required_subfields": ["当前状态：", "已实现内容：", "与原设计差异：", "本次迭代同步点："],
    },
}


def is_folder_manual_file(path: Path) -> bool:
    """判断是否为文件夹说明书。"""
    return path.name == "README.md" or path.name.endswith("_README.md")


def check_required_directories(doc_path: Path) -> Dict:
    required_dirs = [
        "Basic",
        "Basic/PRD",
        "Basic/Architecture",
        "Basic/Database",
        "Basic/API",
        "Basic/Testing",
        "Basic/UI",
        "Framework",
        "Framework/Standards",
        "Framework/CommonCapabilities",
        "Framework/ProblemSolutions",
        "Modules",
        "Modules/_template",
        "DevLogs",
        "DevLogs/errors",
    ]
    result = {"missing": [], "exists": []}
    for dir_name in required_dirs:
        path = doc_path / dir_name
        if path.exists():
            result["exists"].append(dir_name)
        else:
            result["missing"].append(dir_name)
    return result


def check_required_files(doc_path: Path) -> Dict:
    required_files = {
        "00_文档规范.md": doc_path / "00_文档规范.md",
        "Basic/PRD/1_产品概述.md": doc_path / "Basic/PRD/1_产品概述.md",
        "Basic/PRD/3_核心流程.md": doc_path / "Basic/PRD/3_核心流程.md",
        "Basic/Architecture/2_系统架构.md": doc_path / "Basic/Architecture/2_系统架构.md",
        "Basic/Architecture/3_交互时序图.md": doc_path / "Basic/Architecture/3_交互时序图.md",
        "Basic/UI/1_信息架构总览.md": doc_path / "Basic/UI/1_信息架构总览.md",
        "Basic/Testing/1_测试策略.md": doc_path / "Basic/Testing/1_测试策略.md",
        "Framework/Standards/业务模块技术文档规范.md": doc_path / "Framework/Standards/业务模块技术文档规范.md",
        "Framework/Standards/架构模式规范.md": doc_path / "Framework/Standards/架构模式规范.md",
        "Framework/Standards/测试框架规范.md": doc_path / "Framework/Standards/测试框架规范.md",
        "Framework/CommonCapabilities/通用能力文档模板.md": doc_path / "Framework/CommonCapabilities/通用能力文档模板.md",
        "Framework/ProblemSolutions/问题解决方案模板.md": doc_path / "Framework/ProblemSolutions/问题解决方案模板.md",
        "Modules/_template/模块需求文档模板.md": doc_path / "Modules/_template/模块需求文档模板.md",
        "Modules/_template/模块技术文档模板.md": doc_path / "Modules/_template/模块技术文档模板.md",
    }

    result = {"missing": [], "exists": []}
    for name, path in required_files.items():
        if path.exists():
            result["exists"].append(name)
        else:
            result["missing"].append(name)

    tracking_files = sorted(doc_path.glob("DevLogs/v*_执行跟踪.md"))
    if tracking_files:
        result["exists"].append("DevLogs/v*_执行跟踪.md")
    else:
        result["missing"].append("DevLogs/v*_执行跟踪.md")

    todo_files = sorted(doc_path.glob("DevLogs/v*_TODO_01.md"))
    if todo_files:
        result["exists"].append("DevLogs/v*_TODO_01.md")
    else:
        result["missing"].append("DevLogs/v*_TODO_01.md")

    return result


def check_doc_line_counts(doc_path: Path, max_lines: int = 10000) -> Dict:
    result = {"violations": [], "warnings": []}

    for md_file in doc_path.rglob("*.md"):
        if is_folder_manual_file(md_file):
            continue
        try:
            line_count = len(md_file.read_text(encoding="utf-8").splitlines())
        except OSError:
            continue

        relative_path = str(md_file.relative_to(doc_path))
        if line_count > max_lines:
            result["violations"].append(
                {"file": relative_path, "lines": line_count, "suggestion": f"超过 {max_lines} 行，建议拆分"}
            )
        elif line_count > max_lines * 0.8:
            result["warnings"].append(
                {"file": relative_path, "lines": line_count, "suggestion": f"接近 {max_lines} 行，考虑拆分"}
            )

    return result


def check_mermaid_diagrams(doc_path: Path) -> Dict:
    result = {"missing_style": [], "has_style": []}
    for md_file in doc_path.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
        except OSError:
            continue

        if "```mermaid" not in content:
            continue

        relative_path = str(md_file.relative_to(doc_path))
        if "%%{init:" in content or "%%{{init:" in content or "classDef" in content:
            result["has_style"].append(relative_path)
        else:
            result["missing_style"].append(relative_path)
    return result


def has_ascii_block(content: str) -> bool:
    return "```text" in content and "+" in content and "|" in content and "-" in content


def check_ascii_artifacts(doc_path: Path) -> Dict:
    result = {"missing": [], "invalid": [], "valid": []}

    product_overview = doc_path / "Basic/PRD/1_产品概述.md"
    if not product_overview.exists():
        result["missing"].append("产品概述 ASCII 草图")
    else:
        content = product_overview.read_text(encoding="utf-8")
        if "ASCII" in content and has_ascii_block(content):
            result["valid"].append("产品概述 ASCII 草图")
        else:
            result["invalid"].append("产品概述 ASCII 草图")

    requirement_docs = [
        path
        for path in (doc_path / "Modules").rglob("*.md")
        if not is_folder_manual_file(path) and (path.name.endswith("_需求文档.md") or path.name == "模块需求文档模板.md")
    ]
    for md_file in requirement_docs:
        relative_path = str(md_file.relative_to(doc_path))
        try:
            content = md_file.read_text(encoding="utf-8")
        except OSError:
            result["invalid"].append(f"{relative_path}（文件不可读）")
            continue
        if "## 7. 业务 ASCII 交互稿" in content and has_ascii_block(content):
            result["valid"].append(relative_path)
        else:
            result["invalid"].append(relative_path)

    return result


def check_revision_history(doc_path: Path) -> Dict:
    target_dirs = ["Basic", "Framework", "Modules"]
    result = {"missing": [], "valid": []}

    for dir_name in target_dirs:
        for md_file in (doc_path / dir_name).rglob("*.md"):
            if is_folder_manual_file(md_file):
                continue
            try:
                content = md_file.read_text(encoding="utf-8")
            except OSError:
                result["missing"].append(str(md_file.relative_to(doc_path)))
                continue

            relative_path = str(md_file.relative_to(doc_path))
            if "## 文档修订历史" in content and "| 版本 | 日期 | 修订人 | 修订内容 |" in content:
                result["valid"].append(relative_path)
            else:
                result["missing"].append(relative_path)

    return result


def check_module_headers(doc_path: Path) -> Dict:
    result = {
        "missing_metadata": [],
        "missing_requirement_overview": [],
        "missing_requirement_sections": [],
        "missing_technical_manual": [],
        "missing_technical_sections": [],
        "valid": [],
    }
    modules_root = doc_path / "Modules"

    for md_file in modules_root.rglob("*.md"):
        if is_folder_manual_file(md_file):
            continue

        relative_path = str(md_file.relative_to(doc_path))
        try:
            content = md_file.read_text(encoding="utf-8")
        except OSError:
            result["missing_metadata"].append(f"{relative_path}: 文件不可读")
            continue

        missing_fields = [
            field for field in MODULE_METADATA_FIELDS if f"**{field}**：" not in content and f"**{field}**:" not in content
        ]
        if missing_fields:
            result["missing_metadata"].append(f"{relative_path}: 缺少 {', '.join(missing_fields)}")
            continue

        if md_file.name.endswith("_需求文档.md") or md_file.name == "模块需求文档模板.md":
            missing_overview_fields = [field for field in REQUIREMENT_OVERVIEW_FIELDS if field not in content]
            missing_sections = [section for section in REQUIREMENT_REQUIRED_SECTIONS if section not in content]
            if "## 模块概览卡" not in content or missing_overview_fields:
                result["missing_requirement_overview"].append(
                    f"{relative_path}: 缺少 {', '.join(missing_overview_fields) if missing_overview_fields else '模块概览卡标题'}"
                )
                continue
            if missing_sections:
                result["missing_requirement_sections"].append(f"{relative_path}: 缺少 {', '.join(missing_sections)}")
                continue
            result["valid"].append(relative_path)
            continue

        if md_file.name.endswith("_技术文档.md") or md_file.name == "模块技术文档模板.md":
            missing_manual_fields = [field for field in TECHNICAL_MANUAL_FIELDS if field not in content]
            missing_sections = [section for section in TECHNICAL_REQUIRED_SECTIONS if section not in content]
            if "## 模块说明书 (Module Manual)" not in content or missing_manual_fields:
                result["missing_technical_manual"].append(
                    f"{relative_path}: 缺少 {', '.join(missing_manual_fields) if missing_manual_fields else '模块说明书标题'}"
                )
                continue
            if missing_sections:
                result["missing_technical_sections"].append(f"{relative_path}: 缺少 {', '.join(missing_sections)}")
                continue
            result["valid"].append(relative_path)

    return result


def check_framework_archetypes(doc_path: Path) -> Dict:
    result = {"missing": [], "valid": []}
    checks = {
        "Framework/CommonCapabilities/通用能力文档模板.md": CAPABILITY_FIELDS,
        "Framework/ProblemSolutions/问题解决方案模板.md": PROBLEM_SOLUTION_FIELDS,
        "Framework/Standards/测试框架规范.md": ["## 测试分层", "## Agent 验证门禁", "## 反模式"],
    }

    for relative_path, required_fields in checks.items():
        file_path = doc_path / relative_path
        if not file_path.exists():
            result["missing"].append(f"{relative_path}: 文件不存在")
            continue
        try:
            content = file_path.read_text(encoding="utf-8")
        except OSError:
            result["missing"].append(f"{relative_path}: 文件不可读")
            continue

        missing_fields = [field for field in required_fields if field not in content]
        if missing_fields:
            result["missing"].append(f"{relative_path}: 缺少 {', '.join(missing_fields)}")
        else:
            result["valid"].append(relative_path)
    return result


def list_optional_strong_targets(doc_path: Path) -> List[Path]:
    targets: List[Path] = []
    target_dirs = [
        doc_path / "Modules",
        doc_path / "Framework/Standards",
        doc_path / "Framework/CommonCapabilities",
        doc_path / "Framework/ProblemSolutions",
    ]
    for root in target_dirs:
        if not root.exists():
            continue
        for md_file in root.rglob("*.md"):
            if is_folder_manual_file(md_file):
                continue
            targets.append(md_file)
    return sorted(set(targets))


def expected_optional_checks(relative_path: str) -> Dict[str, bool]:
    expectations = {"faq": False, "checklist": False, "code_sync": False, "implementation_status": False}

    if relative_path.startswith("Modules/") and relative_path.endswith("_技术文档.md"):
        expectations.update({"faq": True, "checklist": True, "code_sync": True, "implementation_status": True})
        return expectations

    if relative_path == "Framework/Standards/业务模块技术文档规范.md":
        expectations.update({"faq": True, "checklist": True, "code_sync": True})
        return expectations

    if relative_path == "Framework/Standards/测试框架规范.md":
        expectations.update({"faq": True, "checklist": True})
        return expectations

    if relative_path.startswith("Framework/CommonCapabilities/"):
        expectations.update({"faq": True, "checklist": True})
        return expectations

    if relative_path.startswith("Framework/ProblemSolutions/"):
        expectations.update({"faq": True})

    return expectations


def check_optional_strong_sections(
    doc_path: Path,
    *,
    strict_faq: bool = False,
    strict_checklist: bool = False,
    strict_code_sync: bool = False,
    strict_implementation_status: bool = False,
) -> Dict:
    enabled = {
        "faq": strict_faq,
        "checklist": strict_checklist,
        "code_sync": strict_code_sync,
        "implementation_status": strict_implementation_status,
    }
    result = {
        key: {"enabled": enabled[key], "missing": [], "valid": [], "skipped": []}
        for key in OPTIONAL_STRONG_RULES
    }

    for md_file in list_optional_strong_targets(doc_path):
        relative_path = str(md_file.relative_to(doc_path))
        expectations = expected_optional_checks(relative_path)
        try:
            content = md_file.read_text(encoding="utf-8")
        except OSError:
            for check_name, expected in expectations.items():
                if expected and enabled[check_name]:
                    result[check_name]["missing"].append(f"{relative_path}: 文件不可读")
            continue

        for check_name, config in OPTIONAL_STRONG_RULES.items():
            if not expectations[check_name]:
                continue
            if not enabled[check_name]:
                result[check_name]["skipped"].append(relative_path)
                continue

            matched = any(pattern in content for pattern in config["patterns"])
            if matched and config.get("required_subfields"):
                matched = all(subfield in content for subfield in config["required_subfields"])
            if matched:
                result[check_name]["valid"].append(relative_path)
            else:
                result[check_name]["missing"].append(f"{relative_path}: 缺少 {config['label']}")

    return result


def validate_doc_completeness(
    doc_path: str,
    *,
    strict_faq: bool = False,
    strict_checklist: bool = False,
    strict_code_sync: bool = False,
    strict_implementation_status: bool = False,
) -> Dict:
    doc = Path(doc_path)
    if not doc.exists():
        return {"error": f"文档目录不存在：{doc_path}"}

    return {
        "directories": check_required_directories(doc),
        "files": check_required_files(doc),
        "line_counts": check_doc_line_counts(doc),
        "mermaid": check_mermaid_diagrams(doc),
        "ascii": check_ascii_artifacts(doc),
        "revision_history": check_revision_history(doc),
        "module_headers": check_module_headers(doc),
        "framework_archetypes": check_framework_archetypes(doc),
        "optional_strong_checks": check_optional_strong_sections(
            doc,
            strict_faq=strict_faq,
            strict_checklist=strict_checklist,
            strict_code_sync=strict_code_sync,
            strict_implementation_status=strict_implementation_status,
        ),
    }


def print_validation_report(result: Dict):
    print("\n" + "=" * 60)
    print("📋 文档完整性验证报告")
    print("=" * 60)

    print("\n1️⃣  必需目录检查")
    if result["directories"]["missing"]:
        print(f"   ❌ 缺失 {len(result['directories']['missing'])} 个目录：")
        for item in result["directories"]["missing"]:
            print(f"      - {item}")
    else:
        print(f"   ✅ 所有必需目录已创建 ({len(result['directories']['exists'])} 个)")

    print("\n2️⃣  必需文件检查")
    if result["files"]["missing"]:
        print(f"   ❌ 缺失 {len(result['files']['missing'])} 个文件：")
        for item in result["files"]["missing"]:
            print(f"      - {item}")
    else:
        print(f"   ✅ 所有必需文件已创建 ({len(result['files']['exists'])} 个)")

    print("\n3️⃣  文档行数检查")
    if result["line_counts"]["violations"]:
        print(f"   ❌ {len(result['line_counts']['violations'])} 个文档超过上限：")
        for item in result["line_counts"]["violations"]:
            print(f"      - {item['file']} ({item['lines']} 行)")
    else:
        print("   ✅ 所有文档行数符合规范")

    print("\n4️⃣  Mermaid 图表样式检查")
    if result["mermaid"]["missing_style"]:
        print(f"   ❌ {len(result['mermaid']['missing_style'])} 个 Mermaid 图缺少样式头：")
        for item in result["mermaid"]["missing_style"]:
            print(f"      - {item}")
    else:
        print(f"   ✅ 所有 Mermaid 图表包含样式头 ({len(result['mermaid']['has_style'])} 个)")

    print("\n5️⃣  ASCII 交互稿检查")
    if result["ascii"]["missing"] or result["ascii"]["invalid"]:
        for item in result["ascii"]["missing"]:
            print(f"   ❌ 缺少 ASCII 文档：{item}")
        for item in result["ascii"]["invalid"]:
            print(f"   ❌ ASCII 文档格式异常：{item}")
    else:
        print(f"   ✅ ASCII 交互稿已完整落盘 ({len(result['ascii']['valid'])} 个)")

    print("\n6️⃣  修订历史检查")
    revision = result["revision_history"]
    if revision["missing"]:
        print(f"   ❌ {len(revision['missing'])} 个正式文档缺少修订历史：")
        for item in revision["missing"]:
            print(f"      - {item}")
    else:
        print(f"   ✅ 正式文档均包含修订历史 ({len(revision['valid'])} 个)")

    print("\n7️⃣  模块文档结构检查")
    module_headers = result["module_headers"]
    if (
        module_headers["missing_metadata"]
        or module_headers["missing_requirement_overview"]
        or module_headers["missing_requirement_sections"]
        or module_headers["missing_technical_manual"]
        or module_headers["missing_technical_sections"]
    ):
        for item in module_headers["missing_metadata"]:
            print(f"   ❌ 模块元信息缺失：{item}")
        for item in module_headers["missing_requirement_overview"]:
            print(f"   ❌ 模块概览卡缺失：{item}")
        for item in module_headers["missing_requirement_sections"]:
            print(f"   ❌ 模块需求章节缺失：{item}")
        for item in module_headers["missing_technical_manual"]:
            print(f"   ❌ 模块说明书缺失：{item}")
        for item in module_headers["missing_technical_sections"]:
            print(f"   ❌ 模块技术章节缺失：{item}")
    else:
        print(f"   ✅ 模块文档结构完整 ({len(module_headers['valid'])} 个)")

    print("\n8️⃣  Framework Archetype 检查")
    framework = result["framework_archetypes"]
    if framework["missing"]:
        print(f"   ❌ {len(framework['missing'])} 个 Framework 模板异常：")
        for item in framework["missing"]:
            print(f"      - {item}")
    else:
        print(f"   ✅ Framework 模板结构完整 ({len(framework['valid'])} 个)")

    print("\n9️⃣  可选强校验项")
    optional_checks = result["optional_strong_checks"]
    for check_name, config in OPTIONAL_STRONG_RULES.items():
        check_result = optional_checks[check_name]
        if not check_result["enabled"]:
            print(f"   ⏭️  {config['label']}：未启用强校验")
            continue
        if check_result["missing"]:
            print(f"   ❌ {config['label']} 缺失 {len(check_result['missing'])} 项：")
            for item in check_result["missing"]:
                print(f"      - {item}")
        else:
            print(f"   ✅ {config['label']} 校验通过 ({len(check_result['valid'])} 个)")

    print("\n" + "=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="验证文档完整性")
    parser.add_argument("--doc-path", required=True, help="文档目录路径")
    parser.add_argument("--strict-faq", action="store_true", help="启用 FAQ / 常见问题 强校验")
    parser.add_argument("--strict-checklist", action="store_true", help="启用检查清单强校验")
    parser.add_argument("--strict-code-sync", action="store_true", help="启用代码同步说明强校验")
    parser.add_argument("--strict-implementation-status", action="store_true", help="启用实施现状强校验")
    args = parser.parse_args()

    result = validate_doc_completeness(
        args.doc_path,
        strict_faq=args.strict_faq,
        strict_checklist=args.strict_checklist,
        strict_code_sync=args.strict_code_sync,
        strict_implementation_status=args.strict_implementation_status,
    )
    if "error" in result:
        print(f"❌ {result['error']}", file=sys.stderr)
        sys.exit(1)

    print_validation_report(result)

    has_error = any(
        [
            result["directories"]["missing"],
            result["files"]["missing"],
            result["mermaid"]["missing_style"],
            result["ascii"]["missing"],
            result["ascii"]["invalid"],
            result["revision_history"]["missing"],
            result["module_headers"]["missing_metadata"],
            result["module_headers"]["missing_requirement_overview"],
            result["module_headers"]["missing_requirement_sections"],
            result["module_headers"]["missing_technical_manual"],
            result["module_headers"]["missing_technical_sections"],
            result["framework_archetypes"]["missing"],
            args.strict_faq and result["optional_strong_checks"]["faq"]["missing"],
            args.strict_checklist and result["optional_strong_checks"]["checklist"]["missing"],
            args.strict_code_sync and result["optional_strong_checks"]["code_sync"]["missing"],
            args.strict_implementation_status and result["optional_strong_checks"]["implementation_status"]["missing"],
        ]
    )

    if has_error:
        sys.exit(1)

    print("\n✅ 文档验证通过", file=sys.stderr)


if __name__ == "__main__":
    main()
