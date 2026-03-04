#!/usr/bin/env python3
"""
统一查询 Spec-Driven 文档上下文

为 Agent / tool / MCP 封装提供稳定的结构化查询入口。

使用方法:
    python3 query_doc_context.py --doc-path Documentation --query-type project
    python3 query_doc_context.py --doc-path Documentation --query-type module --name 用户模块
    python3 query_doc_context.py --doc-path Documentation --query-type capability --name 文件处理
    python3 query_doc_context.py --doc-path Documentation --query-type problem --name 异步状态一致性
    python3 query_doc_context.py --doc-path Documentation --query-type suggest-docs --task-text "新增异步导入任务与状态轮询"
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from read_existing_docs import read_existing_docs


TASK_CATEGORY_RULES = {
    "async": ["async", "异步", "并发", "queue", "job", "重试", "retry", "轮询", "poll", "callback", "回调", "后台"],
    "api": ["api", "接口", "contract", "契约", "endpoint", "route", "controller", "handler", "webhook"],
    "data": ["db", "database", "sql", "schema", "表", "字段", "数据", "migration", "repository", "model", "cache", "缓存"],
    "ui": ["ui", "页面", "交互", "view", "screen", "layout", "component", "表单", "列表", "按钮"],
    "testing": ["test", "测试", "e2e", "集成", "integration", "回归", "coverage", "覆盖率", "mock", "fixture"],
    "architecture": ["架构", "architecture", "service", "模块", "module", "依赖", "workflow", "流程", "pipeline", "orchestr"],
    "integration": ["集成", "integration", "remote", "第三方", "third", "rpc", "sdk", "client", "script", "脚本"],
    "workflow": ["导入", "导出", "审批", "审核", "任务", "process", "state", "状态", "流转"],
}

HIGH_RISK_TOKENS = {
    "异步",
    "并发",
    "重试",
    "轮询",
    "回调",
    "锁",
    "竞态",
    "race",
    "cache",
    "缓存",
    "migration",
    "schema",
    "批处理",
    "大文件",
    "上传",
    "下载",
    "导入",
    "导出",
    "支付",
    "权限",
}

MEDIUM_RISK_TOKENS = {
    "api",
    "接口",
    "contract",
    "契约",
    "数据库",
    "表",
    "状态",
    "测试",
    "集成",
    "workflow",
    "流程",
}


def normalize_name(value: str) -> str:
    return value.strip().lower()


def tokenize_text(text: str) -> List[str]:
    lowered = normalize_name(text)
    raw_tokens = re.findall(r"[a-z0-9_]+|[\u4e00-\u9fff]{2,}", lowered)
    stopwords = {"src", "tests", "test", "spec", "file", "path", "md", "py", "ts", "js", "swift"}
    tokens = []
    for token in raw_tokens:
        if len(token) <= 1 or token in stopwords:
            continue
        if all("\u4e00" <= ch <= "\u9fff" for ch in token):
            if len(token) <= 4:
                tokens.append(token)
            tokens.extend([token[i : i + 2] for i in range(len(token) - 1)])
        else:
            tokens.append(token)
    return sorted(set(tokens))


def stringify_values(values) -> str:
    if isinstance(values, list):
        return " ".join(str(item) for item in values)
    return str(values or "")


def compute_overlap(query_tokens: List[str], candidate_text: str) -> Tuple[int, List[str]]:
    candidate = normalize_name(candidate_text)
    hits = []
    score = 0
    for token in query_tokens:
        if token and token in candidate:
            hits.append(token)
            score += max(1, min(len(token), 4))
    return score, sorted(set(hits))


def build_project_summary(doc_context: Dict) -> Dict:
    framework = doc_context.get("framework", {})
    modules = doc_context.get("modules", {})
    return {
        "summary": doc_context.get("summary", ""),
        "counts": {
            "standards": len(framework.get("standards", {})),
            "common_capabilities": len(framework.get("common_capabilities", {})),
            "problem_solutions": len(framework.get("problem_solutions", {})),
            "modules": len(modules),
        },
        "common_capabilities": [
            {
                "name": name,
                "title": item.get("title", ""),
                "summary": item.get("summary", ""),
                "applicable_scenarios": item.get("applicable_scenarios", []),
                "constraints": item.get("constraints", []),
                "is_template": item.get("is_template", False),
            }
            for name, item in sorted(framework.get("common_capabilities", {}).items())
        ],
        "problem_solutions": [
            {
                "name": name,
                "title": item.get("title", ""),
                "summary": item.get("summary", ""),
                "scope": item.get("scope", []),
                "implementation_constraints": item.get("implementation_constraints", []),
                "anti_patterns": item.get("anti_patterns", []),
                "is_template": item.get("is_template", False),
            }
            for name, item in sorted(framework.get("problem_solutions", {}).items())
        ],
        "modules": [
            {
                "name": name,
                "title": item.get("title", ""),
                "version": item.get("version", ""),
                "updated_at": item.get("updated_at", ""),
                "core_function": item.get("core_function", ""),
                "related_modules": item.get("related_modules", []),
            }
            for name, item in sorted(modules.items())
        ],
    }


def suggest_basic_docs(task_text: str) -> List[Dict]:
    normalized = normalize_name(task_text)
    suggestions = []
    rules = [
        (
            "Documentation/Basic/API/1_RESTful_API.md",
            ["api", "接口", "contract", "契约", "endpoint", "route", "路由", "回调"],
            "任务涉及接口或契约变更",
        ),
        (
            "Documentation/Basic/Database/1_数据表设计.md",
            ["db", "database", "sql", "table", "表", "schema", "数据", "migration", "字段", "model"],
            "任务涉及数据结构或存储变更",
        ),
        (
            "Documentation/Basic/UI/1_信息架构总览.md",
            ["ui", "交互", "页面", "screen", "view", "layout", "组件", "按钮", "列表", "表单"],
            "任务涉及界面或交互变更",
        ),
        (
            "Documentation/Basic/Testing/1_测试策略.md",
            ["test", "测试", "e2e", "集成", "回归", "验证", "coverage", "覆盖率"],
            "任务涉及测试或验证要求",
        ),
        (
            "Documentation/Basic/Architecture/2_系统架构.md",
            ["架构", "architecture", "service", "模块", "module", "依赖", "分层", "workflow", "流程"],
            "任务涉及模块边界或架构流转",
        ),
        (
            "Documentation/Basic/PRD/3_核心流程.md",
            ["流程", "process", "业务", "用户", "任务", "导入", "导出", "审核"],
            "任务涉及业务流程或主路径",
        ),
    ]

    for path, keywords, reason in rules:
        hits = [keyword for keyword in keywords if keyword in normalized]
        if hits:
            suggestions.append({"path": path, "score": len(hits), "reason": reason, "matchedTokens": hits[:5]})

    suggestions.sort(key=lambda item: item["score"], reverse=True)
    return suggestions


def score_entries(query_tokens: List[str], entries: Dict[str, Dict], fields: List[str]) -> List[Dict]:
    ranked = []
    for name, entry in entries.items():
        candidate_parts = [name, entry.get("title", "")]
        for field in fields:
            candidate_parts.append(stringify_values(entry.get(field)))
        candidate_text = " ".join(candidate_parts)
        score, hits = compute_overlap(query_tokens, candidate_text)
        if score <= 0:
            continue
        ranked.append(
            {
                "name": name,
                "title": entry.get("title", ""),
                "score": score,
                "matchedTokens": hits[:8],
                "isTemplate": entry.get("is_template", False),
                "summary": entry.get("summary") or entry.get("core_function") or entry.get("position") or "",
            }
        )
    ranked.sort(key=lambda item: (item["isTemplate"], -item["score"], item["name"]))
    return ranked


def infer_task_categories(task_text: str, query_tokens: List[str]) -> List[str]:
    normalized = normalize_name(task_text)
    categories = []
    for category, keywords in TASK_CATEGORY_RULES.items():
        if any(keyword in normalized for keyword in keywords) or any(token in keywords for token in query_tokens):
            categories.append(category)
    return categories


def infer_risk_profile(
    task_text: str,
    query_tokens: List[str],
    task_categories: List[str],
    problem_matches: List[Dict],
    capability_matches: List[Dict],
) -> Dict:
    normalized = normalize_name(task_text)
    high_hits = sorted(
        {
            token
            for token in HIGH_RISK_TOKENS
            if token in normalized or token in query_tokens
        }
    )
    medium_hits = sorted(
        {
            token
            for token in MEDIUM_RISK_TOKENS
            if token in normalized or token in query_tokens
        }
    )
    non_template_problem_matches = [item for item in problem_matches if not item.get("isTemplate")]
    non_template_capability_matches = [item for item in capability_matches if not item.get("isTemplate")]

    if non_template_problem_matches or len(high_hits) >= 2 or "async" in task_categories:
        risk_level = "high"
    elif high_hits or len(medium_hits) >= 2 or {"data", "integration"} & set(task_categories):
        risk_level = "medium"
    else:
        risk_level = "low"

    needs_problem_solution = risk_level in {"high", "medium"} and bool(high_hits or non_template_problem_matches)

    return {
        "riskLevel": risk_level,
        "riskSignals": {
            "high": high_hits[:8],
            "medium": medium_hits[:8],
            "problemMatches": [item["name"] for item in non_template_problem_matches[:3]],
            "capabilityMatches": [item["name"] for item in non_template_capability_matches[:3]],
        },
        "needsProblemSolution": needs_problem_solution,
    }


def build_recommended_read_order(
    recommended: Dict[str, List[str]],
    *,
    risk_level: str,
    needs_problem_solution: bool,
) -> List[Dict]:
    steps: List[Dict] = []
    seen = set()

    def add_entries(paths: List[str], doc_type: str, reason: str):
        for path in paths:
            if not path or path in seen:
                continue
            seen.add(path)
            steps.append(
                {
                    "order": len(steps) + 1,
                    "path": path,
                    "type": doc_type,
                    "reason": reason,
                }
            )

    if recommended.get("targetModules"):
        add_entries(
            recommended["targetModules"],
            "module",
            "先理解目标模块职责、实施现状、上下游依赖和当前版本边界。",
        )
    else:
        add_entries(
            recommended.get("sourceDocs", [])[:2],
            "basic",
            "未明确命中模块文档，先从基础主档建立业务与架构上下文。",
        )

    if needs_problem_solution:
        add_entries(
            recommended.get("problemSolutionRefs", []),
            "problem-solution",
            "任务命中高风险工程问题，编码前先确认反模式、约束和验证方式。",
        )

    add_entries(
        recommended.get("relatedCapabilities", []),
        "capability",
        "确认是否已有通用能力可复用，避免重复造轮子或绕开项目约束。",
    )
    add_entries(
        recommended.get("sourceDocs", []),
        "basic",
        "回查基础文档，确认业务流程、架构约束、接口与数据共识。",
    )

    if risk_level != "low":
        add_entries(
            recommended.get("testSpecs", []),
            "testing",
            "高风险或中风险任务需要提前锁定测试门禁与验证方式。",
        )

    return steps


def suggest_docs(doc_context: Dict, task_text: str) -> Dict:
    framework = doc_context.get("framework", {})
    modules = doc_context.get("modules", {})
    query_tokens = tokenize_text(task_text)

    module_matches = score_entries(
        query_tokens,
        modules,
        ["core_function", "position", "dependencies", "dependents", "related_docs", "related_modules"],
    )
    capability_matches = score_entries(
        query_tokens,
        framework.get("common_capabilities", {}),
        ["core_function", "position", "applicable_scenarios", "constraints", "best_practices", "anti_patterns"],
    )
    problem_matches = score_entries(
        query_tokens,
        framework.get("problem_solutions", {}),
        ["scope", "background", "trigger_scenarios", "anti_patterns", "implementation_constraints", "related_task_types"],
    )
    basic_matches = suggest_basic_docs(task_text)

    recommended = {
        "sourceDocs": [item["path"] for item in basic_matches[:4]],
        "targetModules": [
            f"Documentation/Modules/{item['name']}" if not item["name"].startswith("Documentation/") else item["name"]
            for item in module_matches[:3]
        ],
        "relatedCapabilities": [
            f"Documentation/Framework/CommonCapabilities/{item['name']}"
            for item in capability_matches[:3]
            if not item["isTemplate"]
        ],
        "problemSolutionRefs": [
            f"Documentation/Framework/ProblemSolutions/{item['name']}"
            for item in problem_matches[:3]
            if not item["isTemplate"]
        ],
        "testSpecs": ["Documentation/Basic/Testing/1_测试策略.md"],
    }
    task_categories = infer_task_categories(task_text, query_tokens)
    risk_profile = infer_risk_profile(task_text, query_tokens, task_categories, problem_matches, capability_matches)
    read_order = build_recommended_read_order(
        recommended,
        risk_level=risk_profile["riskLevel"],
        needs_problem_solution=risk_profile["needsProblemSolution"],
    )

    return {
        "queryType": "suggest-docs",
        "taskText": task_text,
        "queryTokens": query_tokens,
        "taskCategory": task_categories,
        "riskLevel": risk_profile["riskLevel"],
        "riskSignals": risk_profile["riskSignals"],
        "needsProblemSolution": risk_profile["needsProblemSolution"],
        "recommendedReadOrder": read_order,
        "recommendedBindings": recommended,
        "basicDocs": basic_matches[:6],
        "modules": module_matches[:6],
        "commonCapabilities": capability_matches[:6],
        "problemSolutions": problem_matches[:6],
    }


def find_named_entry(entries: Dict[str, Dict], name: str) -> Tuple[str, Dict, List[str]]:
    query = normalize_name(name)
    exact_match = None
    partial_matches: List[str] = []

    for entry_name, entry in entries.items():
        title = entry.get("title", "")
        candidates = [entry_name, Path(entry_name).stem, title]
        normalized_candidates = [normalize_name(candidate) for candidate in candidates if candidate]
        if query in normalized_candidates:
            exact_match = entry_name
            break
        if any(query in candidate for candidate in normalized_candidates):
            partial_matches.append(entry_name)

    if exact_match:
        return exact_match, entries[exact_match], partial_matches

    if len(partial_matches) == 1:
        matched_name = partial_matches[0]
        return matched_name, entries[matched_name], partial_matches

    return "", {}, partial_matches


def query_context(doc_path: str, query_type: str, name: str = "") -> Dict:
    doc_context = read_existing_docs(doc_path)
    framework = doc_context.get("framework", {})

    if query_type == "project":
        return {"queryType": query_type, "result": build_project_summary(doc_context)}
    if query_type == "suggest-docs":
        return suggest_docs(doc_context, name)

    buckets = {
        "module": doc_context.get("modules", {}),
        "capability": framework.get("common_capabilities", {}),
        "problem": framework.get("problem_solutions", {}),
        "framework": {
            **framework.get("standards", {}),
            **framework.get("common_capabilities", {}),
            **framework.get("problem_solutions", {}),
        },
    }

    entries = buckets.get(query_type, {})
    if not name:
        return {
            "queryType": query_type,
            "available": sorted(entries.keys()),
            "count": len(entries),
        }

    matched_name, matched_entry, partial_matches = find_named_entry(entries, name)
    if matched_name:
        return {
            "queryType": query_type,
            "matched": matched_name,
            "result": matched_entry,
            "alternatives": [item for item in partial_matches if item != matched_name],
        }

    return {
        "queryType": query_type,
        "matched": None,
        "result": None,
        "alternatives": partial_matches,
        "message": f"未找到与 {name} 匹配的 {query_type} 文档",
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="统一查询 Spec-Driven 文档上下文")
    parser.add_argument("--doc-path", required=True, help="Documentation 目录路径")
    parser.add_argument(
        "--query-type",
        required=True,
        choices=["project", "module", "capability", "problem", "framework", "suggest-docs"],
        help="查询类型",
    )
    parser.add_argument("--name", help="文档名、模块名或关键字")
    parser.add_argument("--task-text", help="任务描述，用于 suggest-docs")
    parser.add_argument("--output", help="输出 JSON 文件路径（可选）")
    args = parser.parse_args()

    query_input = args.name or ""
    if args.query_type == "suggest-docs":
        query_input = args.task_text or query_input
        if not query_input:
            parser.error("suggest-docs 模式必须提供 --task-text 或 --name")

    result = query_context(args.doc_path, args.query_type, query_input)
    output = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"✅ 查询结果已保存到：{args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
