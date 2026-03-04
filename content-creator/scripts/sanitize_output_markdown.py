#!/usr/bin/env python3
"""
最终发布稿 Markdown 清洗工具

用途：
1. 删除作者辅助性的截图指引块
2. 按需删除 Markdown 图片占位符
3. 按需将草稿中的图片路径统一转换为 Output/{platform}/images/ 相对路径格式

设计原则：
- draft / image_plan 可以保留作者辅助信息
- article.md 必须尽量干净，不依赖 Agent 手工删除固定标记
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SCREENSHOT_GUIDE_RE = re.compile(r"^\s*>\s*💡\s*\*\*截图指引\*\*：", re.MULTILINE)
IMAGE_PLACEHOLDER_LINE_RE = re.compile(r"^\s*!\[\[(AI生图|待截图|AI封面图)\].*\)\s*$")
PATH_REWRITES = (
    (re.compile(r"\]\(\s*(?:\./)?Materials/Medias/images/"), "](images/"),
    (re.compile(r"\]\(\s*(?:\./)?Medias/images/"), "](images/"),
)


def remove_screenshot_guides(text: str) -> str:
    lines = text.splitlines()
    cleaned: list[str] = []
    skip_following_blockquotes = False

    for line in lines:
        if SCREENSHOT_GUIDE_RE.match(line):
            skip_following_blockquotes = True
            continue

        if skip_following_blockquotes:
            if line.lstrip().startswith(">"):
                continue
            skip_following_blockquotes = False

        cleaned.append(line)

    return "\n".join(cleaned)


def strip_image_placeholders(text: str) -> str:
    lines = text.splitlines()
    kept = [line for line in lines if not IMAGE_PLACEHOLDER_LINE_RE.match(line)]
    return "\n".join(kept)


def rewrite_image_paths(text: str) -> str:
    rewritten = text
    for pattern, replacement in PATH_REWRITES:
        rewritten = pattern.sub(replacement, rewritten)
    return rewritten


def normalize_blank_lines(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def sanitize_markdown(
    text: str,
    *,
    strip_guides: bool,
    strip_placeholders: bool,
    rewrite_paths: bool,
) -> str:
    cleaned = text

    if strip_guides:
        cleaned = remove_screenshot_guides(cleaned)
    if strip_placeholders:
        cleaned = strip_image_placeholders(cleaned)
    if rewrite_paths:
        cleaned = rewrite_image_paths(cleaned)

    return normalize_blank_lines(cleaned)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="清洗用于最终发布的 Markdown 文件。")
    parser.add_argument("--input", required=True, help="输入 Markdown 文件路径")
    parser.add_argument("--output", help="输出 Markdown 文件路径；默认回写到输入文件")
    parser.add_argument(
        "--strip-screenshot-guides",
        action="store_true",
        help="删除截图指引引用块（推荐用于 article.md）",
    )
    parser.add_argument(
        "--strip-image-placeholders",
        action="store_true",
        help="删除 Markdown 图片占位符行（适合 short_form / visual_first 的 article.md）",
    )
    parser.add_argument(
        "--rewrite-image-paths",
        action="store_true",
        help="将 Materials/Medias/images 或 Medias/images 路径重写为 images/ 相对路径",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve() if args.output else input_path

    if not input_path.exists():
        raise SystemExit(f"输入文件不存在: {input_path}")

    source = input_path.read_text(encoding="utf-8")
    cleaned = sanitize_markdown(
        source,
        strip_guides=args.strip_screenshot_guides,
        strip_placeholders=args.strip_image_placeholders,
        rewrite_paths=args.rewrite_image_paths,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(cleaned, encoding="utf-8")

    print(f"✅ Markdown 已清洗: {output_path}")
    print(
        "   - 删除截图指引: "
        f"{'是' if args.strip_screenshot_guides else '否'}\n"
        "   - 删除图片占位: "
        f"{'是' if args.strip_image_placeholders else '否'}\n"
        "   - 改写图片路径: "
        f"{'是' if args.rewrite_image_paths else '否'}"
    )


if __name__ == "__main__":
    main()
