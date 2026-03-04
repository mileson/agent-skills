#!/usr/bin/env python3
"""
本地占位扫描工具

用途：
1. 扫描 Markdown 中的正文图片占位
2. 扫描文章头部的 AI封面图占位
3. 支持 content-creator 工作区三链路主文件自动解析
3. 输出 dry-run 任务清单，不调用任何生图 API
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


INLINE_IMAGE_RE = re.compile(r"!\[\[(.*?)\]\(([^)]+)\)")

COMMENT_BLOCK_RE = re.compile(r"<!--\s*AI封面图\s*(.*?)-->", re.DOTALL)
SUPPORTED_ASPECT_RATIOS = {
    "1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1", "4:3",
    "4:5", "5:4", "8:1", "9:16", "16:9", "21:9",
    # 兼容旧稿解析，执行时不会再继续使用这个比例。
    "2.35:1",
}
PROMPTISH_KEYWORDS = (
    "无文字",
    "电影级",
    "赛博朋克",
    "编辑风",
    "cinematic",
    "editorial",
    "高细节",
    "光影",
    "质感",
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


def pick_latest(candidates: list[Path]) -> Path | None:
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def resolve_scan_target(target: Path, platform: str | None) -> tuple[Path, str]:
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
                f"工作区模式只扫描最终产物；如果你要扫描草稿，请直接传入具体 Markdown 文件路径。"
            )
        return markdown_file, route

    markdown_file = target / "Output" / platform / "article.md"
    if not markdown_file.exists():
        raise SystemExit(
            f"未找到平台 `{platform}` 的最终正文主文件: {markdown_file}。"
            f"工作区模式只扫描最终产物；如果你要扫描草稿，请直接传入具体 Markdown 文件路径。"
        )
    return markdown_file, route


def looks_like_aspect_ratio(value: str) -> bool:
    return value.strip() in SUPPORTED_ASPECT_RATIOS


def is_prompt_like_caption(caption: str) -> bool:
    normalized = caption.strip()
    if not normalized:
        return False
    if len(normalized) > 16:
        return True
    if "，" in normalized or "," in normalized or "。" in normalized:
        return True
    lower = normalized.lower()
    return any(keyword in normalized or keyword in lower for keyword in PROMPTISH_KEYWORDS)


def safe_caption(caption: str) -> str:
    normalized = caption.strip()
    if not normalized or is_prompt_like_caption(normalized):
        return ""
    return normalized


def parse_comment_fields(raw: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in raw.splitlines():
        cleaned = line.strip()
        if not cleaned or ":" not in cleaned:
            continue
        key, value = cleaned.split(":", 1)
        fields[key.strip()] = value.strip()
    return fields


def split_inline_placeholder(inner: str) -> tuple[str, list[str], str] | None:
    markers = ("AI生图", "待截图", "AI封面图")
    marker = next((value for value in markers if inner.startswith(value)), None)
    if not marker:
        return None

    rest = inner[len(marker):]
    if rest.startswith("]"):
        rest = rest[1:]
    segments: list[str] = []
    while rest.startswith("["):
        end = rest.find("]")
        if end == -1:
            break
        segments.append(rest[1:end].strip())
        rest = rest[end + 1 :]
    return marker, segments, rest.strip()


def parse_inline_placeholder(inner: str, output: str, line: int, source: str = "markdown_image") -> dict | None:
    parsed = split_inline_placeholder(inner)
    if not parsed:
        return None

    marker, segments, prompt = parsed
    item = {
        "line": line,
        "source": source,
        "marker": marker,
        "output": output.strip(),
        "caption": "",
        "prompt": prompt.strip(),
        "description": prompt.strip(),
    }

    if marker == "AI封面图":
        platform = segments[0] if len(segments) >= 1 else ""
        aspect_ratio = segments[1] if len(segments) >= 2 else ""
        caption = segments[2] if len(segments) >= 3 else ""
        if len(segments) == 2 and not looks_like_aspect_ratio(aspect_ratio):
            caption = aspect_ratio
            aspect_ratio = ""
        item.update(
            {
                "type": "cover",
                "platform": platform.strip(),
                "aspect_ratio": aspect_ratio.strip(),
                "caption": caption.strip(),
                "should_generate": True,
            }
        )
        return item

    if marker == "AI生图":
        caption = ""
        aspect_ratio = ""
        if len(segments) >= 2:
            caption = segments[0]
            aspect_ratio = segments[1]
        elif len(segments) == 1:
            if looks_like_aspect_ratio(segments[0]):
                aspect_ratio = segments[0]
            else:
                caption = segments[0]
        item.update(
            {
                "type": "inline_ai_image",
                "platform": "",
                "aspect_ratio": aspect_ratio.strip(),
                "caption": caption.strip(),
                "should_generate": True,
            }
        )
        return item

    description = prompt.strip() or (segments[0].strip() if segments else "")
    item.update(
        {
            "type": "manual_screenshot",
            "platform": "",
            "aspect_ratio": "",
            "caption": "",
            "prompt": description,
            "description": description,
            "should_generate": False,
        }
    )
    return item


def parse_image_placeholders(lines: list[str]) -> list[dict]:
    tasks: list[dict] = []
    for idx, line in enumerate(lines, start=1):
        for match in INLINE_IMAGE_RE.finditer(line):
            inner, output = match.groups()
            item = parse_inline_placeholder(inner, output, idx)
            if item:
                tasks.append(item)
    return tasks


def parse_cover_comment_blocks(text: str) -> list[dict]:
    tasks: list[dict] = []
    for match in COMMENT_BLOCK_RE.finditer(text):
        raw = match.group(1)
        start_line = text[:match.start()].count("\n") + 1
        fields = parse_comment_fields(raw)

        tasks.append(
            {
                "line": start_line,
                "source": "html_comment",
                "marker": "AI封面图",
                "type": "cover",
                "platform": fields.get("platform", ""),
                "aspect_ratio": fields.get("aspect_ratio", ""),
                "caption": fields.get("caption", ""),
                "prompt": fields.get("prompt", ""),
                "description": fields.get("prompt", ""),
                "output": fields.get("output", ""),
                "should_generate": True,
            }
        )
    return tasks


def render_markdown(tasks: list[dict], markdown_file: Path, route: str) -> str:
    mode_label = "具体文件模式" if route == "direct_file" else "工作区最终产物模式"
    lines = [
        "# 占位扫描结果",
        "",
        f"- 文件: `{markdown_file}`",
        f"- 模式: `{mode_label}`",
        f"- 解析模式: `{route}`",
        f"- 总占位数: **{len(tasks)}**",
        f"- AI 生成任务: **{sum(1 for x in tasks if x['should_generate'])}**",
        f"- 手动截图任务: **{sum(1 for x in tasks if not x['should_generate'])}**",
        "",
        "## 任务清单",
        "",
    ]

    for i, task in enumerate(tasks, start=1):
        lines.append(f"### {i}. {task['type']}")
        lines.append(f"- 行号: `{task['line']}`")
        lines.append(f"- 标记: `{task['marker']}`")
        lines.append(f"- 来源: `{task['source']}`")
        if task.get("platform"):
            lines.append(f"- 平台: `{task['platform']}`")
        if task.get("aspect_ratio"):
            lines.append(f"- 比例: `{task['aspect_ratio']}`")
        lines.append(f"- 输出路径: `{task['output']}`")
        if task.get("caption"):
            lines.append(f"- 图注: `{task['caption']}`")
        lines.append(f"- 提示词: `{task.get('prompt') or task['description']}`")
        lines.append(f"- 需生成: `{'yes' if task['should_generate'] else 'no'}`")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="扫描 Markdown 中的 AI 生图/封面图占位，不调用真实 API。")
    parser.add_argument("target", help="待扫描的 Markdown 文件路径，或 content-creator 工作区目录路径")
    parser.add_argument("--platform", help="当 target 为工作区目录时必填，用于按 workflow_route 自动定位主文件")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="输出格式")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    markdown_file, route = resolve_scan_target(target, args.platform)
    if not markdown_file.exists():
        raise SystemExit(f"文件不存在: {markdown_file}")

    text = markdown_file.read_text(encoding="utf-8")
    lines = text.splitlines()

    tasks = parse_image_placeholders(lines)
    tasks.extend(parse_cover_comment_blocks(text))
    tasks.sort(key=lambda x: (x["line"], x["source"]))

    result = {
        "file": str(markdown_file),
        "route": route,
        "total": len(tasks),
        "tasks": tasks,
    }

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(tasks, markdown_file, route))


if __name__ == "__main__":
    main()
