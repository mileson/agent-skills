#!/usr/bin/env python3
"""
根据代码变更建议应更新的 Spec 文档

用于 Spec-Driven 的文档反写阶段，先给出建议更新范围和原因，
再由 Agent 或人工决定是否实际修改对应文档。

使用方法:
    python3 suggest_doc_updates.py --doc-path Documentation --changed-file src/api/user.py
    python3 suggest_doc_updates.py --doc-path Documentation --changed-file src/tasks/executor.py --task-text "新增后台任务重试"
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List

from query_doc_context import query_context
from read_existing_docs import read_existing_docs


def normalize_path_tokens(path: str) -> List[str]:
    normalized = path.lower().replace("\\", "/")
    tokens = re.findall(r"[a-z0-9_]+|[\u4e00-\u9fff]{2,}", normalized)
    return sorted(set(token for token in tokens if len(token) > 1))


def build_change_text(changed_files: List[str], task_text: str = "") -> str:
    parts = list(changed_files)
    if task_text:
        parts.append(task_text)
    return " ".join(parts)


def infer_basic_doc_updates(changed_files: List[str]) -> List[Dict]:
    rules = [
        ("Documentation/Basic/API/1_RESTful_API.md", ["api", "route", "controller", "handler", "endpoint", "contract"], "检测到接口/路由相关代码变更"),
        ("Documentation/Basic/Database/1_数据表设计.md", ["db", "database", "migration", "schema", "model", "repository", "sql"], "检测到数据结构或存储相关代码变更"),
        ("Documentation/Basic/UI/1_信息架构总览.md", ["ui", "view", "screen", "page", "component", "layout"], "检测到界面/交互相关代码变更"),
        ("Documentation/Basic/Testing/1_测试策略.md", ["test", "spec", "e2e", "integration", "fixture"], "检测到测试相关代码变更"),
        ("Documentation/Basic/Architecture/2_系统架构.md", ["service", "module", "workflow", "executor", "orchestr", "pipeline"], "检测到服务编排或模块边界相关代码变更"),
    ]

    detected = []
    path_text = " ".join(changed_files).lower()
    for doc_path, keywords, reason in rules:
        hits = [keyword for keyword in keywords if keyword in path_text]
        if hits:
            detected.append({"path": doc_path, "reason": reason, "matchedTokens": hits[:5]})
    return detected


def infer_module_updates(doc_context: Dict, changed_files: List[str]) -> List[Dict]:
    modules = doc_context.get("modules", {})
    suggestions = []
    path_text = " ".join(changed_files).lower()

    for name, item in modules.items():
        candidates = [name, item.get("title", ""), item.get("core_function", "")]
        related_modules = item.get("related_modules", [])
        candidates.extend(related_modules)
        hits = []
        for candidate in candidates:
            normalized_candidate = str(candidate).lower()
            if normalized_candidate and normalized_candidate in path_text:
                hits.append(candidate)
        if hits:
            suggestions.append(
                {
                    "path": f"Documentation/Modules/{name}",
                    "reason": "变更路径中命中模块名或模块关系词",
                    "matchedTokens": hits[:5],
                }
            )
    return suggestions


def suggest_doc_updates(doc_path: str, changed_files: List[str], task_text: str = "") -> Dict:
    doc_context = read_existing_docs(doc_path)
    change_text = build_change_text(changed_files, task_text)
    suggested = query_context(doc_path, "suggest-docs", change_text)

    basic_updates = infer_basic_doc_updates(changed_files)
    module_updates = infer_module_updates(doc_context, changed_files)

    recommended = suggested.get("recommendedBindings", {})
    capability_updates = [
        {
            "path": path,
            "reason": "变更内容与通用能力推荐匹配，需确认能力文档是否已同步实现",
        }
        for path in recommended.get("relatedCapabilities", [])
    ]
    problem_updates = [
        {
            "path": path,
            "reason": "变更内容命中高风险问题类型，需确认问题方案是否需要追加修订历史或新约束",
        }
        for path in recommended.get("problemSolutionRefs", [])
    ]

    deduped = {}
    for item in basic_updates + module_updates + capability_updates + problem_updates:
        deduped.setdefault(item["path"], item)

    return {
        "queryType": "suggest-doc-updates",
        "changedFiles": changed_files,
        "taskText": task_text,
        "taskCategory": suggested.get("taskCategory", []),
        "riskLevel": suggested.get("riskLevel", "unknown"),
        "needsProblemSolution": suggested.get("needsProblemSolution", False),
        "recommendedReadOrder": suggested.get("recommendedReadOrder", []),
        "suggestedUpdates": list(deduped.values()),
        "recommendedBindings": recommended,
        "evidence": {
            "basicDocs": suggested.get("basicDocs", []),
            "modules": suggested.get("modules", []),
            "commonCapabilities": suggested.get("commonCapabilities", []),
            "problemSolutions": suggested.get("problemSolutions", []),
        },
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="根据代码变更建议应更新的 Spec 文档")
    parser.add_argument("--doc-path", required=True, help="Documentation 目录路径")
    parser.add_argument("--changed-file", action="append", dest="changed_files", help="变更文件路径，可重复传入")
    parser.add_argument("--task-text", help="任务描述（可选）")
    parser.add_argument("--output", help="输出 JSON 文件路径（可选）")
    args = parser.parse_args()

    if not args.changed_files:
        parser.error("至少提供一个 --changed-file")

    result = suggest_doc_updates(args.doc_path, args.changed_files, args.task_text or "")
    output = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"✅ 建议结果已保存到：{args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
