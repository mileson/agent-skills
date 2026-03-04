#!/usr/bin/env python3
"""
文章配图单入口：
1. 解析主文件（支持具体文件 / content-creator 工作区 + 平台）
2. 扫描 AI 图片占位
3. 按风格分组执行 generate_image.py
4. 执行完成后自动回写占位为普通图片引用
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from scan_placeholders import (
    parse_cover_comment_blocks,
    parse_image_placeholders,
    resolve_scan_target,
    safe_caption,
)


def choose_style(task: dict, style_cover: str, style_diagram: str, style_scene: str) -> str:
    if task.get("type") == "cover":
        return style_cover

    desc = (task.get("prompt") or task.get("description") or "").lower()
    diagram_keywords = [
        "流程", "工作流", "架构", "图解", "看板", "面板", "模块", "系统", "任务",
        "分发", "调度", "pipeline", "workflow", "architecture", "diagram", "dashboard",
        "panel", "module", "system", "task", "agent", "cron", "log",
    ]
    if any(keyword in desc for keyword in diagram_keywords):
        return style_diagram
    return style_scene


def load_tasks(markdown_file: Path) -> list[dict]:
    text = markdown_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    tasks = parse_image_placeholders(lines)
    tasks.extend(parse_cover_comment_blocks(text))
    tasks.sort(key=lambda x: (x["line"], x["source"]))
    return [task for task in tasks if task.get("should_generate") and task.get("output")]


def find_workspace_root(markdown_file: Path) -> Path:
    for candidate in [markdown_file.parent, *markdown_file.parents]:
        if (candidate / "Materials").exists() or (candidate / "Output").exists():
            return candidate
    return markdown_file.parent


def resolve_output_path(markdown_file: Path, raw_path: str) -> str:
    ref = Path(raw_path)
    if ref.is_absolute():
        return str(ref)

    direct = (markdown_file.parent / ref).resolve()
    workspace_root = find_workspace_root(markdown_file)
    workspace_ref = (workspace_root / ref).resolve()

    if raw_path.startswith("Materials/") or raw_path.startswith("Output/"):
        return str(workspace_ref)
    return str(direct)


def build_grouped_tasks(tasks: list[dict], style_cover: str, style_diagram: str, style_scene: str) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for task in tasks:
        style = choose_style(task, style_cover, style_diagram, style_scene)
        groups[style].append(task)
    return groups


def run_generate_group(
    style: str,
    tasks: list[dict],
    provider: str,
    resolution: str,
    force: bool,
) -> None:
    script = Path(__file__).resolve().parent / "generate_image.py"
    cmd = [
        sys.executable,
        str(script),
        "--prompt",
        "--style",
        style,
        "--provider",
        provider,
        "--resolution",
        resolution,
    ]
    prompts = [task.get("prompt") or task["description"] for task in tasks]
    outputs = [task["output"] for task in tasks]
    aspect_ratios = [(task.get("aspect_ratio") or "16:9") for task in tasks]
    cmd.extend(prompts)
    cmd.extend(["--output", *outputs, "--aspect_ratio", *aspect_ratios])
    if force:
        cmd.append("--force")

    print(f"\n=== 执行风格组: {style} ({len(tasks)} 个任务) ===")
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="文章配图单入口：扫描 + 生图 + 占位回写")
    parser.add_argument("target", help="Markdown 文件路径，或 content-creator 工作区目录路径")
    parser.add_argument("--platform", help="当 target 为工作区目录时必填")
    parser.add_argument("--provider", choices=["auto", "apimart", "openrouter"], default="auto")
    parser.add_argument("--resolution", choices=["0.5K", "1K", "2K", "4K"], default="1K")
    parser.add_argument("--style-cover", default="brand_concept", help="封面默认风格")
    parser.add_argument("--style-diagram", default="corporate_diagram", help="流程/结构类图片默认风格")
    parser.add_argument("--style-scene", default="metaphorical_scene", help="场景/隐喻类图片默认风格")
    parser.add_argument("--force", action="store_true", help="强制重新生成，忽略已存在输出")
    parser.add_argument("--dry-run", action="store_true", help="只输出任务与分组计划，不实际生图")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    markdown_file, route = resolve_scan_target(target, args.platform)
    tasks = load_tasks(markdown_file)
    for task in tasks:
        task["output"] = resolve_output_path(markdown_file, task["output"])

    if not tasks:
        print(
            "ℹ️ 未发现需要 AI 执行的图片任务\n"
            f"- 文件: {markdown_file}\n"
            f"- 解析模式: {route}"
        )
        return

    groups = build_grouped_tasks(tasks, args.style_cover, args.style_diagram, args.style_scene)

    print("📋 配图执行计划")
    print(f"- 文件: {markdown_file}")
    print(f"- 解析模式: {route}")
    print(f"- 任务总数: {len(tasks)}")
    for style, style_tasks in groups.items():
        print(f"- 风格 `{style}`: {len(style_tasks)} 个")
        for task in style_tasks:
            caption = task.get("caption") or ""
            warning = ""
            if not safe_caption(caption):
                warning = " | 图注=缺失或不合规"
            print(
                f"  • {task['type']} | 比例={task.get('aspect_ratio') or '16:9'} | "
                f"图注={caption or '（空）'} | 输出={task['output']} | 提示词={task.get('prompt') or task['description']}{warning}"
            )

    if args.dry_run:
        print("🧪 dry-run 模式：未执行任何生图或回写。")
        return

    for style, style_tasks in groups.items():
        run_generate_group(
            style=style,
            tasks=style_tasks,
            provider=args.provider,
            resolution=args.resolution,
            force=args.force,
        )

    consume_script = Path(__file__).resolve().parent / "consume_generated_placeholders.py"
    consume_cmd = [sys.executable, str(consume_script), str(target)]
    if target.is_dir() and args.platform:
        consume_cmd.extend(["--platform", args.platform])

    print("\n=== 回写已完成占位 ===")
    subprocess.run(consume_cmd, check=True)
    print("\n🎉 单入口执行完成：扫描、生图、占位回写已全部完成。")


if __name__ == "__main__":
    main()
