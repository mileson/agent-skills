#!/usr/bin/env python3
"""
初始化 content-creator 工作区。

用途：
1. 在任意目录下，根据已确认的选题自动创建本次内容创作工作区
2. 生成标准目录结构、origin.md 种子文件和 workspace.config.yaml
3. 让用户不必手动 mkdir 再进入工作流
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import List

from yaml_utils import save_workspace_config_yaml


INVALID_CHARS_PATTERN = re.compile(r'[\\/:*?"<>|]+')
SPACE_PATTERN = re.compile(r"\s+")


def sanitize_workspace_name(topic: str) -> str:
    """将选题转换为可作为目录名的工作区名称，尽量保留中文可读性。"""
    name = topic.strip()
    name = INVALID_CHARS_PATTERN.sub("-", name)
    name = SPACE_PATTERN.sub(" ", name)
    name = name.strip(". ").strip()
    return name[:80] or "未命名选题"


def ensure_unique_dir(base_dir: Path, workspace_name: str) -> Path:
    """避免目录冲突，必要时追加序号。"""
    candidate = base_dir / workspace_name
    if not candidate.exists():
        return candidate

    for index in range(2, 100):
        next_candidate = base_dir / f"{workspace_name}-{index}"
        if not next_candidate.exists():
            return next_candidate

    raise RuntimeError(f"无法为工作区分配唯一目录名: {workspace_name}")


def parse_platforms(raw: str | None) -> List[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def build_seed_origin(topic: str, platforms: List[str], seed_text: str | None) -> str:
    platform_text = "、".join(platforms) if platforms else "待确认"
    seed_body = seed_text.strip() if seed_text else "请在这里补充本次内容创作的原始素材、观点、案例、数据和截图说明。"
    return f"""# 原始素材

## 选题
{topic}

## 目标平台
{platform_text}

## 需求摘要
{seed_body}

## 待补充素材
- 背景信息：
- 关键事实：
- 案例或数据：
- 需要截图的内容：
- 其他备注：
"""


def build_delivery_config(platforms: List[str]) -> dict:
    """为每个目标平台生成默认交付模式配置。"""
    return {
        "platforms": {
            platform: {
                "mode": "auto_format",
            }
            for platform in platforms
        }
    }


def init_workspace(
    base_dir: Path,
    topic: str,
    platforms: List[str],
    seed_text: str | None,
    description: str | None,
) -> Path:
    workspace_name = sanitize_workspace_name(topic)
    workspace_dir = ensure_unique_dir(base_dir, workspace_name)

    materials_dir = workspace_dir / "Materials"
    images_dir = materials_dir / "Medias" / "images"
    output_dir = workspace_dir / "Output"
    drafts_dir = output_dir / "_drafts"
    reports_dir = output_dir / "_reports"

    images_dir.mkdir(parents=True, exist_ok=True)
    drafts_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    for platform in platforms:
        (output_dir / platform / "images").mkdir(parents=True, exist_ok=True)

    origin_file = materials_dir / "origin.md"
    origin_file.write_text(
        build_seed_origin(topic=topic, platforms=platforms, seed_text=seed_text),
        encoding="utf-8",
    )

    config = {
        "workspace": {
            "name": workspace_name,
            "created_at": datetime.now().isoformat(),
            "description": description or f"基于选题《{topic}》自动初始化的内容创作工作区",
        },
        "materials": {
            "primary_source": "Materials/origin.md",
            "total_word_count": 0,
            "files": ["origin.md"],
        },
        "medias": {
            "images": {
                "count": 0,
                "total_size": "0MB",
                "files": [],
            }
        },
        "target_platforms": platforms,
        "creation": {
            "mode": "collaborative",
        },
        "delivery": build_delivery_config(platforms),
        "generation_status": "initialized",
        "history": [
            {
                "stage": "workspace_initialization",
                "completed_at": datetime.now().isoformat(),
                "notes": f"基于选题《{topic}》自动创建工作区",
            }
        ],
        "outputs": {
            "drafts": [],
            "platforms": {
                platform: [f"Output/{platform}/article.md", f"Output/{platform}/images/"]
                for platform in platforms
            },
        },
        "meta": {
            "version": "1.0",
            "generator": "content-creator.init_workspace",
        },
    }
    save_workspace_config_yaml(config, str(workspace_dir))
    return workspace_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="初始化 content-creator 工作区")
    parser.add_argument("--base-dir", default=".", help="工作区父目录，默认当前目录")
    parser.add_argument("--topic", required=True, help="已确认的选题名称")
    parser.add_argument("--platforms", help="目标平台列表，逗号分隔，如 xhs,wechat")
    parser.add_argument("--seed-text", help="写入 Materials/origin.md 的需求摘要或素材摘要")
    parser.add_argument("--description", help="工作区描述")
    args = parser.parse_args()

    base_dir = Path(args.base_dir).expanduser().resolve()
    base_dir.mkdir(parents=True, exist_ok=True)

    workspace_dir = init_workspace(
        base_dir=base_dir,
        topic=args.topic,
        platforms=parse_platforms(args.platforms),
        seed_text=args.seed_text,
        description=args.description,
    )

    print("✅ 工作区初始化完成")
    print(f"📁 工作区目录: {workspace_dir}")
    print(f"📝 主素材文件: {workspace_dir / 'Materials' / 'origin.md'}")
    print(f"⚙️ 配置文件: {workspace_dir / 'workspace.config.yaml'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
