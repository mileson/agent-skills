#!/usr/bin/env python3
"""
将已完成的 AI 图片占位回写为普通 Markdown 图片引用。

支持两种输入模式：
1. 直接传具体 Markdown 文件
2. 传 content-creator 工作区目录 + --platform

处理规则：
- `AI封面图` / `[AI生图]`：如果目标图片已存在，则回写为普通图片引用
- `[待截图]`：始终保持不动
- `AI封面图` 注释块：如果目标图片已存在，则改写为普通图片引用
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scan_placeholders import (
    COMMENT_BLOCK_RE,
    INLINE_IMAGE_RE,
    parse_comment_fields,
    parse_inline_placeholder,
    safe_caption,
)


def load_platform_routes() -> dict[str, str]:
    skill_dir = Path(__file__).resolve().parent.parent
    config_path = skill_dir.parent / "content-creator" / "templates" / "platform_styles_lib.json"
    if not config_path.exists():
        return {}

    data = json.loads(config_path.read_text(encoding="utf-8"))
    routes: dict[str, str] = {}
    for platform in data.get("platforms", []):
        platform_id = platform.get("id")
        route = platform.get("workflow_route")
        if platform_id and route:
            routes[platform_id] = route
    return routes


def resolve_target(target: Path, platform: str | None) -> tuple[Path, str]:
    if target.is_file():
        return target, "direct_file"

    if not target.is_dir():
        raise SystemExit(f"目标不存在或不是文件/目录: {target}")

    if not platform:
        raise SystemExit("当传入工作区目录时，必须通过 --platform 指定平台，例如：--platform xhs")

    routes = load_platform_routes()
    route = routes.get(platform)
    if not route:
        raise SystemExit(f"无法从 content-creator 平台配置中找到平台 `{platform}` 的 workflow_route")

    if route == "visual_first":
        markdown_file = target / "Output" / platform / "image_plan.md"
        if not markdown_file.exists():
            raise SystemExit(
                f"未找到 visual_first 最终图片主文件: {markdown_file}。"
                "工作区模式只处理最终产物；如果你要处理草稿，请直接传入具体 Markdown 文件路径。"
            )
        return markdown_file, route

    markdown_file = target / "Output" / platform / "article.md"
    if not markdown_file.exists():
        raise SystemExit(
            f"未找到平台 `{platform}` 的最终正文主文件: {markdown_file}。"
            "工作区模式只处理最终产物；如果你要处理草稿，请直接传入具体 Markdown 文件路径。"
        )
    return markdown_file, route


def find_workspace_root(markdown_file: Path) -> Path:
    for candidate in [markdown_file.parent, *markdown_file.parents]:
        if (candidate / "Materials").exists() or (candidate / "Output").exists():
            return candidate
    return markdown_file.parent


def resolve_asset_path(markdown_file: Path, raw_path: str) -> Path:
    ref = Path(raw_path)
    if ref.is_absolute():
        return ref

    direct = (markdown_file.parent / ref).resolve()
    if direct.exists():
        return direct

    workspace_root = find_workspace_root(markdown_file)
    workspace_ref = (workspace_root / ref).resolve()
    if workspace_ref.exists():
        return workspace_ref

    return direct


def make_plain_image(caption: str, output: str) -> str:
    alt = safe_caption(caption)
    return f"![{alt}]({output})"


def consume_markdown_images(text: str, markdown_file: Path) -> tuple[str, int]:
    replacements = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal replacements
        inner, output = match.groups()
        parsed = parse_inline_placeholder(inner, output, line=0)
        if not parsed or parsed["marker"] == "待截图":
            return match.group(0)

        output_path = resolve_asset_path(markdown_file, output.strip())
        if not output_path.exists():
            return match.group(0)

        replacements += 1
        return make_plain_image(parsed.get("caption", ""), output.strip())

    return INLINE_IMAGE_RE.sub(replace, text), replacements


def consume_cover_comments(text: str, markdown_file: Path) -> tuple[str, int]:
    replacements = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal replacements
        fields = parse_comment_fields(match.group(1))
        output = fields.get("output", "").strip()
        if not output:
            return match.group(0)

        output_path = resolve_asset_path(markdown_file, output)
        if not output_path.exists():
            return match.group(0)

        replacements += 1
        return make_plain_image(fields.get("caption", ""), output)

    return COMMENT_BLOCK_RE.sub(replace, text), replacements


def main() -> None:
    parser = argparse.ArgumentParser(description="将已生成的 AI 图片占位回写成普通 Markdown 图片引用。")
    parser.add_argument("target", help="待处理的 Markdown 文件路径，或 content-creator 工作区目录路径")
    parser.add_argument("--platform", help="当 target 为工作区目录时必填，用于按 workflow_route 自动定位主文件")
    parser.add_argument("--output", help="输出 Markdown 文件路径；默认回写到输入文件")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    markdown_file, route = resolve_target(target, args.platform)
    text = markdown_file.read_text(encoding="utf-8")

    consumed_text, markdown_count = consume_markdown_images(text, markdown_file)
    consumed_text, comment_count = consume_cover_comments(consumed_text, markdown_file)

    output_path = Path(args.output).expanduser().resolve() if args.output else markdown_file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(consumed_text, encoding="utf-8")

    print(
        "✅ 已完成占位回写\n"
        f"- 文件: {markdown_file}\n"
        f"- 模式: {'具体文件模式' if route == 'direct_file' else '工作区最终产物模式'}\n"
        f"- Markdown 图片占位回写数: {markdown_count}\n"
        f"- AI封面图注释块回写数: {comment_count}\n"
        f"- 输出: {output_path}"
    )


if __name__ == "__main__":
    main()
