#!/usr/bin/env python3
"""
根据代码变更生成修订历史草案

用于 Spec-Driven 的文档反写阶段，基于变更文件、任务描述和文档推荐结果，
为相关文档生成可直接复用的修订历史表格行与代码同步说明草案。

使用方法:
    python3 generate_revision_history_draft.py \
      --doc-path Documentation \
      --changed-file src/api/task_callback.py \
      --changed-file tests/integration/test_task_callback.py \
      --task-text "新增后台任务回调与状态轮询" \
      --version v1.3 \
      --author AI助手
"""

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List

from query_doc_context import query_context
from suggest_doc_updates import suggest_doc_updates


DOC_FOCUS_RULES = [
    ("Documentation/Basic/API/", ["同步接口 / Contract 定义", "更新请求响应约束与回调语义"]),
    ("Documentation/Basic/Database/", ["同步数据结构与持久化约束", "补充字段、状态或迁移说明"]),
    ("Documentation/Basic/UI/", ["同步界面交互与状态呈现", "更新 ASCII 交互稿或关键交互约束"]),
    ("Documentation/Basic/Testing/", ["补充测试门禁与验证范围", "同步单元 / 集成 / E2E 覆盖要求"]),
    ("Documentation/Basic/Architecture/", ["更新模块边界与调用流程", "同步关键约束与依赖关系"]),
    ("Documentation/Basic/PRD/", ["同步业务流程或需求边界", "更新主路径与场景约束"]),
    ("Documentation/Modules/", ["同步模块实施现状与关键流程", "更新模块依赖、风险与待办"]),
    ("Documentation/Framework/CommonCapabilities/", ["同步通用能力输入输出与复用边界", "补充约束、最佳实践或反模式"]),
    ("Documentation/Framework/ProblemSolutions/", ["同步问题方案约束与验证方式", "补充反模式、触发场景或标准解法"]),
    ("Documentation/Framework/Standards/", ["同步团队规范或门禁规则", "补充实现要求与审查清单"]),
]


def normalize_path_tokens(path: str) -> List[str]:
    normalized = path.lower().replace("\\", "/")
    tokens = re.findall(r"[a-z0-9_]+|[\u4e00-\u9fff]{2,}", normalized)
    return sorted(set(token for token in tokens if len(token) > 1))


def extract_diff_highlights(diff_text: str) -> List[str]:
    highlights = []
    patterns = [
        (r"^\+\s*(?:def|async def|function|export function)\s+([A-Za-z0-9_]+)", "新增/调整函数 {name}"),
        (r"^\+\s*(?:class|export class|interface|type|enum)\s+([A-Za-z0-9_]+)", "新增/调整结构 {name}"),
        (r"^\+\s*@(?:app|router)\.(get|post|put|delete|patch)\(", "新增/调整路由 {name}"),
    ]
    for line in diff_text.splitlines():
        for pattern, template in patterns:
            match = re.search(pattern, line)
            if match:
                highlights.append(template.format(name=match.group(1)))
                break
        if len(highlights) >= 6:
            break
    return highlights


def run_git_diff(git_repo: str, changed_files: List[str]) -> str:
    if not git_repo:
        return ""

    repo_path = Path(git_repo)
    if not repo_path.exists():
        return ""

    repo_files = []
    for file_path in changed_files:
        path = Path(file_path)
        if path.is_absolute():
            try:
                repo_files.append(str(path.resolve().relative_to(repo_path.resolve())))
                continue
            except ValueError:
                pass
        repo_files.append(file_path)

    try:
        status_result = subprocess.run(
            ["git", "-C", str(repo_path), "status", "--short", "--", *repo_files],
            check=False,
            capture_output=True,
            text=True,
        )
        untracked = set()
        if status_result.returncode == 0:
            for line in status_result.stdout.splitlines():
                if not line.startswith("?? "):
                    continue
                tracked_path = line[3:].strip()
                if tracked_path:
                    untracked.add(tracked_path)

        result = subprocess.run(
            ["git", "-C", str(repo_path), "diff", "--unified=0", "HEAD", "--", *repo_files],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return ""

    if result.returncode not in (0, 1):
        return ""

    diff_parts = [result.stdout.strip()] if result.stdout.strip() else []
    for relative_path in sorted(untracked):
        file_path = repo_path / relative_path
        if not file_path.exists():
            continue
        lines = file_path.read_text(encoding="utf-8").splitlines()
        synthetic = [
            f"diff --git a/{relative_path} b/{relative_path}",
            "new file mode 100644",
            f"--- /dev/null",
            f"+++ b/{relative_path}",
        ]
        synthetic.extend(f"+{line}" for line in lines[:200])
        diff_parts.append("\n".join(synthetic))

    return "\n".join(part for part in diff_parts if part).strip()


def infer_git_repo(changed_files: List[str]) -> str:
    for file_path in changed_files:
        path = Path(file_path)
        probe = path if path.is_dir() else path.parent
        if not probe:
            continue
        try:
            result = subprocess.run(
                ["git", "-C", str(probe), "rev-parse", "--show-toplevel"],
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError:
            return ""
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    return ""


def summarize_diff_by_file(diff_text: str) -> List[Dict]:
    files: List[Dict] = []
    current = None

    def ensure_current(path: str):
        nonlocal current
        current = {
            "path": path,
            "symbols": [],
            "routes": [],
            "tests": [],
            "states": [],
            "keywords": [],
        }
        files.append(current)

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            match = re.search(r" b/(.+)$", line)
            if match:
                ensure_current(match.group(1))
            continue

        if current is None:
            continue

        if not line.startswith(("+", "-")) or line.startswith(("+++", "---")):
            continue

        symbol_patterns = [
            r"(?:def|async def|function|export function)\s+([A-Za-z0-9_]+)",
            r"(?:class|export class|interface|type|enum)\s+([A-Za-z0-9_]+)",
        ]
        for pattern in symbol_patterns:
            match = re.search(pattern, line)
            if match:
                symbol = match.group(1)
                if symbol not in current["symbols"]:
                    current["symbols"].append(symbol)

        route_match = re.search(r"(?:@(?:app|router)|(?:app|router))\.(get|post|put|delete|patch)\(", line, re.IGNORECASE)
        if route_match:
            method = route_match.group(1).upper()
            if method not in current["routes"]:
                current["routes"].append(method)

        if re.search(r"\b(test_[A-Za-z0-9_]+|describe|it|test)\b", line):
            snippet = re.sub(r"^[+-]\s*", "", line).strip()
            if snippet and snippet not in current["tests"]:
                current["tests"].append(snippet[:120])

        if any(keyword in line.lower() for keyword in ["status", "state", "retry", "poll", "callback", "queue", "executor"]):
            snippet = re.sub(r"^[+-]\s*", "", line).strip()
            if snippet and snippet not in current["states"]:
                current["states"].append(snippet[:120])

        keyword_hits = []
        for keyword in ["api", "route", "contract", "schema", "migration", "cache", "retry", "callback", "poll", "test", "integration"]:
            if keyword in line.lower():
                keyword_hits.append(keyword)
        for keyword in keyword_hits:
            if keyword not in current["keywords"]:
                current["keywords"].append(keyword)

    return files


def infer_change_dimensions(changed_files: List[str], task_text: str) -> Dict[str, List[str]]:
    combined = " ".join(changed_files + [task_text]).lower()
    rules = {
        "接口/契约": ["api", "route", "controller", "handler", "contract", "callback", "webhook"],
        "数据结构": ["db", "database", "sql", "schema", "migration", "model", "repository", "cache"],
        "界面交互": ["ui", "view", "screen", "page", "component", "layout", "form"],
        "测试验证": ["test", "spec", "e2e", "integration", "fixture", "coverage"],
        "异步执行": ["async", "retry", "poll", "callback", "queue", "job", "executor", "后台", "异步", "轮询", "重试"],
        "流程编排": ["workflow", "pipeline", "orchestr", "module", "service", "state", "流程", "状态", "任务"],
        "文件处理": ["file", "upload", "download", "stream", "import", "export", "上传", "下载", "导入", "导出"],
    }

    dimensions = {}
    for label, keywords in rules.items():
        hits = [keyword for keyword in keywords if keyword in combined]
        if hits:
            dimensions[label] = hits[:5]
    return dimensions


def summarize_task(task_text: str, changed_files: List[str]) -> str:
    if task_text.strip():
        return task_text.strip()
    file_names = [Path(path).name for path in changed_files[:3]]
    return "同步代码变更：" + "、".join(file_names)


def doc_focus_points(doc_path: str) -> List[str]:
    for prefix, focus_points in DOC_FOCUS_RULES:
        if doc_path.startswith(prefix):
            return focus_points
    return ["同步本次实现差异", "补充与代码一致的约束说明"]


def build_revision_content(
    doc_path: str,
    task_summary: str,
    dimensions: Dict[str, List[str]],
    diff_highlights: List[str],
    diff_by_file: List[Dict],
    reason: str,
) -> str:
    points = []
    for focus in doc_focus_points(doc_path):
        if focus not in points:
            points.append(focus)

    for dimension in list(dimensions.keys())[:2]:
        item = f"补充 {dimension} 相关说明"
        if item not in points:
            points.append(item)

    for highlight in diff_highlights[:2]:
        if highlight not in points:
            points.append(highlight)

    for item in diff_by_file[:2]:
        file_name = Path(item["path"]).name
        detail_parts = []
        if item["symbols"]:
            detail_parts.append("涉及 " + " / ".join(item["symbols"][:2]))
        if item["routes"]:
            detail_parts.append("路由方法 " + " / ".join(item["routes"][:2]))
        if item["tests"]:
            detail_parts.append("补充测试断言")
        if item["states"]:
            detail_parts.append("调整状态/回调逻辑")
        if detail_parts:
            points.append(f"同步 {file_name}：{'，'.join(detail_parts)}")

    if reason:
        reason_text = reason.replace("检测到", "").replace("命中", "").strip("： ")
        if reason_text:
            points.append(reason_text)

    numbered_points = [f"{index}) {point}" for index, point in enumerate(points[:5], start=1)]
    return f"基于代码变更同步（{task_summary}）：{'；'.join(numbered_points)}"


def build_code_sync_note(doc_path: str, revision_content: str, changed_files: List[str], diff_by_file: List[Dict]) -> str:
    if not (
        doc_path.startswith("Documentation/Modules/")
        or doc_path.startswith("Documentation/Framework/")
    ):
        return ""

    file_names = "、".join(Path(path).name for path in changed_files[:5])
    details = []
    for item in diff_by_file[:3]:
        file_name = Path(item["path"]).name
        segments = []
        if item["symbols"]:
            segments.append("核心符号：" + " / ".join(item["symbols"][:3]))
        if item["routes"]:
            segments.append("路由：" + " / ".join(item["routes"][:3]))
        if item["states"]:
            segments.append("状态逻辑已调整")
        if item["tests"]:
            segments.append("测试已补充")
        if segments:
            details.append(f"{file_name}（{'；'.join(segments)}）")

    details_text = "；".join(details)
    if details_text:
        return f"本次基于实际代码实现同步：{revision_content}。对应变更文件包括：{file_names}。细粒度同步点：{details_text}。"
    return f"本次基于实际代码实现同步：{revision_content}。对应变更文件包括：{file_names}。"


def escape_table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def generate_revision_history_draft(
    doc_path: str,
    changed_files: List[str],
    *,
    task_text: str = "",
    version: str = "待定版本",
    author: str = "AI助手",
    draft_date: str = "",
    diff_text: str = "",
    git_repo: str = "",
) -> Dict:
    doc_suggestions = suggest_doc_updates(doc_path, changed_files, task_text)
    doc_query = query_context(doc_path, "suggest-docs", task_text or " ".join(changed_files))
    draft_date = draft_date or date.today().isoformat()
    task_summary = summarize_task(task_text, changed_files)
    git_repo = git_repo or infer_git_repo(changed_files)
    if not diff_text and git_repo:
        diff_text = run_git_diff(git_repo, changed_files)
    dimensions = infer_change_dimensions(changed_files, task_text)
    diff_highlights = extract_diff_highlights(diff_text)
    diff_by_file = summarize_diff_by_file(diff_text)

    drafts = []
    for suggestion in doc_suggestions.get("suggestedUpdates", []):
        target_path = suggestion["path"]
        reason = suggestion.get("reason", "")
        revision_content = build_revision_content(
            target_path,
            task_summary,
            dimensions,
            diff_highlights,
            diff_by_file,
            reason,
        )
        markdown_row = (
            f"| {escape_table_cell(version)} | {escape_table_cell(draft_date)} | "
            f"{escape_table_cell(author)} | {escape_table_cell(revision_content)} |"
        )
        code_sync_note = build_code_sync_note(target_path, revision_content, changed_files, diff_by_file)

        drafts.append(
            {
                "path": target_path,
                "reason": reason,
                "revisionContent": revision_content,
                "markdownTableRow": markdown_row,
                "codeSyncNote": code_sync_note,
            }
        )

    overall_summary_parts = list(dimensions.keys())[:4]
    if diff_highlights:
        overall_summary_parts.extend(diff_highlights[:2])

    return {
        "queryType": "generate-revision-history-draft",
        "docPath": doc_path,
        "changedFiles": changed_files,
        "taskText": task_text,
        "version": version,
        "date": draft_date,
        "author": author,
        "gitRepo": git_repo,
        "taskCategory": doc_query.get("taskCategory", []),
        "riskLevel": doc_query.get("riskLevel", "unknown"),
        "needsProblemSolution": doc_query.get("needsProblemSolution", False),
        "changeDimensions": dimensions,
        "diffHighlights": diff_highlights,
        "diffByFile": diff_by_file,
        "revisionHistoryDrafts": drafts,
        "overallRevisionSummary": {
            "headline": f"基于代码变更同步：{task_summary}",
            "highlights": overall_summary_parts,
        },
        "recommendedReadOrder": doc_query.get("recommendedReadOrder", []),
        "recommendedBindings": doc_suggestions.get("recommendedBindings", {}),
        "suggestedDocUpdates": doc_suggestions.get("suggestedUpdates", []),
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="根据代码变更生成修订历史草案")
    parser.add_argument("--doc-path", required=True, help="Documentation 目录路径")
    parser.add_argument("--changed-file", action="append", dest="changed_files", help="变更文件路径，可重复传入")
    parser.add_argument("--task-text", help="任务描述（可选）")
    parser.add_argument("--version", default="待定版本", help="修订版本号（默认：待定版本）")
    parser.add_argument("--author", default="AI助手", help="修订人（默认：AI助手）")
    parser.add_argument("--date", dest="draft_date", help="修订日期（默认：今天）")
    parser.add_argument("--diff-file", help="可选的 unified diff 文本文件路径")
    parser.add_argument("--git-repo", help="可选的 Git 仓库路径，用于自动抓取真实 diff")
    parser.add_argument("--output", help="输出 JSON 文件路径（可选）")
    args = parser.parse_args()

    if not args.changed_files:
        parser.error("至少提供一个 --changed-file")

    diff_text = ""
    if args.diff_file:
        diff_text = Path(args.diff_file).read_text(encoding="utf-8")

    result = generate_revision_history_draft(
        args.doc_path,
        args.changed_files,
        task_text=args.task_text or "",
        version=args.version,
        author=args.author,
        draft_date=args.draft_date or "",
        diff_text=diff_text,
        git_repo=args.git_repo or "",
    )
    output = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"✅ 修订历史草案已保存到：{args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
