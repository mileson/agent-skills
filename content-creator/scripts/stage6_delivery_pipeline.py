#!/usr/bin/env python3
"""
Stage 6 交付单入口：
1. 读取 workspace.config.yaml 中的平台交付模式
2. 复制 Materials/Medias/images 到 Output/{platform}/images
3. 生成最终 article.md（以及 visual_first 的 image_plan.md）
4. 调用 article-illustrator 单入口完成 AI 图片执行
5. 对微信公众号自动执行 markdown-to-wechat
6. 按配置决定是否继续调用 content-publisher
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from yaml_utils import load_workspace_config_yaml


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ROOT_SKILLS_DIR = SKILL_DIR.parent
PLATFORM_RULES_FILE = SKILL_DIR / "templates" / "platform_styles_lib.json"
SANITIZE_SCRIPT = SCRIPT_DIR / "sanitize_output_markdown.py"
ILLUSTRATION_PIPELINE = ROOT_SKILLS_DIR / "article-illustrator" / "scripts" / "run_illustration_pipeline.py"
MARKDOWN_TO_WECHAT = ROOT_SKILLS_DIR / "markdown-to-wechat" / "convert.sh"
PUBLISHER = ROOT_SKILLS_DIR / "content-publisher" / "scripts" / "publisher.py"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
CREATION_MODES = {"collaborative", "autonomous"}
PUBLISH_SUPPORTED_PLATFORMS = {"wechat", "jike"}


def load_platform_rules() -> dict[str, dict[str, Any]]:
    payload = json.loads(PLATFORM_RULES_FILE.read_text(encoding="utf-8"))
    return {item["id"]: item for item in payload.get("platforms", [])}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stage 6 交付单入口")
    parser.add_argument("workspace", help="工作区目录")
    parser.add_argument("--platform", help="只处理单个平台；默认处理 workspace.config.yaml 中全部目标平台")
    parser.add_argument("--force-images", action="store_true", help="强制重新生成 AI 图片")
    parser.add_argument("--wechat-theme", default="deep-blue", help="微信公众号 HTML 转换主题")
    parser.add_argument("--dry-run", action="store_true", help="只输出执行计划，不真正执行")
    return parser.parse_args()


def run_cmd(cmd: list[str], *, dry_run: bool, cwd: Path | None = None) -> None:
    rendered = " ".join(cmd)
    print(f"$ {rendered}")
    if dry_run:
        return
    subprocess.run(cmd, check=True, cwd=str(cwd) if cwd else None)


def run_cmd_capture_json(cmd: list[str], *, dry_run: bool, cwd: Path | None = None) -> dict[str, Any] | None:
    rendered = " ".join(cmd)
    print(f"$ {rendered}")
    if dry_run:
        return None
    result = subprocess.run(
        cmd,
        check=True,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
    )
    stdout = result.stdout.strip()
    if not stdout:
        return {}
    return json.loads(stdout)


def list_source_images(workspace_dir: Path) -> list[Path]:
    src_dir = workspace_dir / "Materials" / "Medias" / "images"
    if not src_dir.exists():
        return []
    return sorted(p for p in src_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS)


def copy_source_images(workspace_dir: Path, platform: str, *, dry_run: bool) -> list[str]:
    copied: list[str] = []
    src_images = list_source_images(workspace_dir)
    dst_dir = workspace_dir / "Output" / platform / "images"
    dst_dir.mkdir(parents=True, exist_ok=True)
    for src in src_images:
        dst = dst_dir / src.name
        copied.append(str(dst))
        print(f"  - copy {src.name} -> Output/{platform}/images/{src.name}")
        if not dry_run:
            shutil.copy2(src, dst)
    return copied


def find_latest_file(directory: Path, patterns: list[str]) -> Path | None:
    matches: list[Path] = []
    for pattern in patterns:
        matches.extend(sorted(directory.glob(pattern)))
    if not matches:
        return None
    matches = sorted({p.resolve() for p in matches})
    return Path(matches[-1])


def resolve_draft_file(workspace_dir: Path, platform: str) -> Path:
    drafts_dir = workspace_dir / "Output" / "_drafts"
    optimized = find_latest_file(drafts_dir, [f"05_draft_optimized_v2.{platform}.*.md"])
    if optimized:
        return optimized
    draft = find_latest_file(drafts_dir, [f"04_draft.{platform}.*.md"])
    if draft:
        return draft
    raise FileNotFoundError(f"未找到 {platform} 的 04/05 draft 文件")


def resolve_delivery_mode(config: dict[str, Any], platform: str) -> str:
    return (
        config.get("delivery", {})
        .get("platforms", {})
        .get(platform, {})
        .get("mode", "auto_format")
    )


def resolve_creation_mode(config: dict[str, Any]) -> str:
    mode = (config.get("creation", {}) or {}).get("mode", "collaborative")
    if mode in CREATION_MODES:
        return mode
    print(f"⚠️ 未识别的 creation.mode={mode}，已回退为 collaborative")
    return "collaborative"


def build_warning(platform: str, code: str, message: str) -> dict[str, Any]:
    return {
        "at": datetime.now().isoformat(),
        "platform": platform,
        "stage": "stage6_delivery_pipeline",
        "code": code,
        "message": message,
    }


def ensure_image_plan_output(workspace_dir: Path, platform: str, *, dry_run: bool) -> Path | None:
    plan_src = workspace_dir / "Output" / "_drafts" / f"03_image_plan.{platform}.md"
    if not plan_src.exists():
        return None
    plan_dst = workspace_dir / "Output" / platform / "image_plan.md"
    print(f"  - sync image_plan -> Output/{platform}/image_plan.md")
    if not dry_run:
        plan_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(plan_src, plan_dst)
    return plan_dst


def sanitize_article(
    workspace_dir: Path,
    platform: str,
    workflow_route: str,
    draft_file: Path,
    *,
    dry_run: bool,
) -> Path:
    output_file = workspace_dir / "Output" / platform / "article.md"
    cmd = [
        sys.executable,
        str(SANITIZE_SCRIPT),
        "--input",
        str(draft_file),
        "--output",
        str(output_file),
        "--strip-screenshot-guides",
    ]
    if workflow_route == "long_form":
        cmd.append("--rewrite-image-paths")
    else:
        cmd.append("--strip-image-placeholders")
    run_cmd(cmd, dry_run=dry_run)
    return output_file


def run_illustration(
    workspace_dir: Path,
    platform: str,
    *,
    force_images: bool,
    dry_run: bool,
) -> None:
    cmd = [
        sys.executable,
        str(ILLUSTRATION_PIPELINE),
        str(workspace_dir),
        "--platform",
        platform,
    ]
    if force_images:
        cmd.append("--force")
    if dry_run:
        cmd.append("--dry-run")
    run_cmd(cmd, dry_run=dry_run)


def run_markdown_to_wechat(workspace_dir: Path, *, theme: str, dry_run: bool) -> Path:
    input_file = workspace_dir / "Output" / "wechat" / "article.md"
    output_file = workspace_dir / "Output" / "wechat" / "article.html"
    cmd = [
        str(MARKDOWN_TO_WECHAT),
        str(input_file),
        "--theme",
        theme,
        "-o",
        str(output_file),
    ]
    run_cmd(cmd, dry_run=dry_run)
    return output_file


def run_publisher(workspace_dir: Path, platform: str, *, dry_run: bool) -> dict[str, Any] | None:
    cmd = [
        sys.executable,
        str(PUBLISHER),
        "publish",
        "--platform",
        platform,
        "--workspace",
        str(workspace_dir),
    ]
    return run_cmd_capture_json(cmd, dry_run=dry_run)


def resolve_quality_score(workspace_dir: Path, platform: str) -> str:
    drafts_dir = workspace_dir / "Output" / "_drafts"
    score_file = find_latest_file(drafts_dir, [f"05_quality_score.{platform}.*.md"])
    if not score_file or not score_file.exists():
        return "未记录"
    content = score_file.read_text(encoding="utf-8")
    match = re.search(r"(\d+(?:\.\d+)?)\s*/\s*10", content)
    if match:
        return f"{match.group(1)}/10"
    return "未记录"


def build_delivery_record(summary: dict[str, Any]) -> dict[str, Any]:
    publish_result = summary.get("publish_result") or {}
    status = "formatted"
    if summary["delivery_mode"] == "auto_format_and_publish":
        publish_status = publish_result.get("status")
        if publish_status in {"success", "draft_created"}:
            status = "published"
        else:
            status = "publish_skipped"

    record: dict[str, Any] = {
        "executed_at": datetime.now().isoformat(),
        "mode": summary["delivery_mode"],
        "workflow_route": summary["workflow_route"],
        "status": status,
        "quality_score": summary.get("quality_score", "未记录"),
        "outputs": {
            "article": "./article.md",
            "images_dir": "./images/",
            "metadata": "./metadata.yaml",
        },
    }
    if summary.get("html_rel"):
        record["outputs"]["html"] = "./article.html"
    if summary.get("image_plan_rel"):
        record["outputs"]["image_plan"] = "./image_plan.md"

    if publish_result:
        record["publish"] = {
            key: value
            for key, value in publish_result.items()
            if key in {"status", "message", "draft_id", "publish_id", "url"}
        }
    warnings = summary.get("warnings") or []
    if warnings:
        record["warnings"] = [{"code": item["code"], "message": item["message"]} for item in warnings]

    return record


def write_delivery_record(workspace_dir: Path, platform: str, summary: dict[str, Any], *, dry_run: bool) -> None:
    if dry_run:
        return

    metadata_path = workspace_dir / "Output" / platform / "metadata.yaml"
    if not metadata_path.exists():
        return

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = yaml.safe_load(f) or {}

    record = build_delivery_record(summary)
    metadata["last_delivery"] = copy.deepcopy(record)
    records = metadata.get("delivery_records")
    if not isinstance(records, list):
        records = []
    records.append(copy.deepcopy(record))
    metadata["delivery_records"] = records

    with open(metadata_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(metadata, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def build_workspace_delivery_summary(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    executed_at = datetime.now().isoformat()
    platforms: list[dict[str, Any]] = []
    modes: list[str] = []

    for summary in summaries:
        platform_entry: dict[str, Any] = {
            "platform": summary["platform"],
            "mode": summary["delivery_mode"],
            "workflow_route": summary["workflow_route"],
            "quality_score": summary.get("quality_score", "未记录"),
            "outputs": {
                "article": summary["article_rel"],
                "images_dir": summary["images_rel"],
                "metadata": summary["metadata_rel"],
            },
        }
        if summary.get("html_rel"):
            platform_entry["outputs"]["html"] = summary["html_rel"]
        if summary.get("image_plan_rel"):
            platform_entry["outputs"]["image_plan"] = summary["image_plan_rel"]
        if summary.get("publish_result"):
            platform_entry["publish"] = {
                key: value
                for key, value in (summary["publish_result"] or {}).items()
                if key in {"status", "message", "draft_id", "publish_id", "url"}
            }
        warnings = summary.get("warnings") or []
        if warnings:
            platform_entry["warnings"] = [{"code": item["code"], "message": item["message"]} for item in warnings]
        modes.append(summary["delivery_mode"])
        platforms.append(platform_entry)

    overall_mode = "mixed" if len(set(modes)) > 1 else (modes[0] if modes else "unknown")
    published = False
    for item in platforms:
        publish = item.get("publish") or {}
        if publish.get("status") in {"success", "draft_created"}:
            published = True
            break
    overall_status = "published" if published else "formatted"

    return {
        "executed_at": executed_at,
        "mode": overall_mode,
        "status": overall_status,
        "platforms": platforms,
    }


def write_workspace_delivery_summary(workspace_dir: Path, summaries: list[dict[str, Any]], *, dry_run: bool) -> None:
    if dry_run or not summaries:
        return

    reports_dir = workspace_dir / "Output" / "_reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    summary_path = reports_dir / "delivery-summary.yaml"

    if summary_path.exists():
        with open(summary_path, "r", encoding="utf-8") as f:
            payload = yaml.safe_load(f) or {}
    else:
        payload = {}

    run_record = build_workspace_delivery_summary(summaries)
    payload["last_run"] = copy.deepcopy(run_record)
    records = payload.get("run_records")
    if not isinstance(records, list):
        records = []
    records.append(copy.deepcopy(run_record))
    payload["run_records"] = records

    with open(summary_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def write_autonomous_warning_report(
    workspace_dir: Path,
    summaries: list[dict[str, Any]],
    *,
    creation_mode: str,
    dry_run: bool,
) -> None:
    if dry_run or creation_mode != "autonomous":
        return

    warnings: list[dict[str, Any]] = []
    for summary in summaries:
        warnings.extend(summary.get("warnings") or [])
    if not warnings:
        return

    reports_dir = workspace_dir / "Output" / "_reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / "autonomous-run-report.md"

    header = "# 自动化运行报告\n\n> 记录自动创作模式下的 warning（不中断执行）。\n\n"
    if report_path.exists():
        content = report_path.read_text(encoding="utf-8")
        if not content.startswith("# 自动化运行报告"):
            content = header + content
    else:
        content = header

    executed_at = datetime.now().isoformat()
    lines = [
        f"## 运行记录 - {executed_at}",
        "- creation.mode: autonomous",
        f"- 记录条数: {len(warnings)}",
        "",
    ]
    for index, item in enumerate(warnings, start=1):
        lines.append(f"{index}. [{item['platform']}] `{item['code']}` - {item['message']}")
    lines.append("")

    report_path.write_text(content + "\n".join(lines), encoding="utf-8")


def render_platform_summary(summary: dict[str, Any]) -> None:
    platform = summary["platform"]
    mode = summary["delivery_mode"]
    article_rel = summary["article_rel"]
    images_rel = summary["images_rel"]
    metadata_rel = summary["metadata_rel"]
    html_rel = summary.get("html_rel")
    quality_score = summary.get("quality_score", "未记录")
    extra_outputs = summary.get("extra_outputs", [])
    publish_result = summary.get("publish_result") or {}
    creation_mode = summary.get("creation_mode", "collaborative")
    warnings = summary.get("warnings", [])
    dry_run = summary.get("dry_run", False)

    print("\n✅ 内容创作完成")
    print(f"\n📊 质量评分：{quality_score}")
    print("\n📦 已完成本地交付包：")
    print(f"\n### {platform}")
    print(f"- 交付模式：delivery.platforms.{platform}.mode = {mode}")
    print(f"- 正文：{article_rel}")
    print(f"- 图片：{images_rel}")
    print(f"- metadata：{metadata_rel}")
    if html_rel:
        print(f"- HTML：{html_rel}")
    for line in extra_outputs:
        print(f"- {line}")
    if warnings:
        if creation_mode == "autonomous":
            print("- warning：本次存在非阻断告警，详情见 Output/_reports/autonomous-run-report.md")
        else:
            print("- warning：本次存在非阻断告警（协同模式不写入自动化运行报告）")

    if mode == "auto_format":
        status = "✅ 已完成本地交付包"
        if dry_run:
            status = "📝 dry-run：预览本地交付包"
        print(f"- 状态：{status}")
        print("\n📌 后续状态")
        if dry_run:
            print("- 当前为 dry-run，仅预览 Stage 6 执行计划，未实际写入产物")
        else:
            print("- 当前模式只完成本地格式化与交付产物构建")
        print("- 不再提示用户手动调用某个 Skill")
        return

    status = "✅ 已完成格式化并继续自动发布"
    if dry_run:
        status = "📝 dry-run：预览格式化与自动发布"
    print(f"- 状态：{status}")
    print("- 发布凭证由 content-publisher 通过 secrets-vault 获取")

    print("\n🚀 发布结果")
    print(f"- 平台：{platform}")
    if dry_run:
        print("- 执行动作：dry-run 预览")
        print("- 结果：未实际调用 content-publisher")
        return

    if platform == "wechat":
        publish_action = "创建公众号草稿"
    elif platform == "jike":
        publish_action = "发布即刻动态"
    else:
        publish_action = "调用平台发布接口"

    result_status = publish_result.get("status", "unknown")
    if platform == "wechat":
        result_summary = "草稿创建成功" if result_status in {"success", "draft_created"} else publish_result.get("message", "执行完成")
    elif platform == "jike":
        result_summary = "动态发布成功" if result_status == "success" else publish_result.get("message", "执行完成")
    else:
        result_summary = publish_result.get("message", "执行完成")

    print(f"- 执行动作：{publish_action}")
    print(f"- 结果：{result_summary}")
    if publish_result.get("draft_id"):
        print(f"- 草稿ID：{publish_result['draft_id']}")
    if publish_result.get("publish_id"):
        print(f"- 发布ID：{publish_result['publish_id']}")
    if publish_result.get("url"):
        print(f"- 链接：{publish_result['url']}")
    print("\n📌 后续状态")
    print("- 当前模式已自动继续执行 content-publisher")
    print("- 回复中直接汇报平台结果，不再提示用户手动执行发布")


def target_platforms(config: dict[str, Any], only_platform: str | None) -> list[str]:
    platforms = config.get("target_platforms", [])
    if only_platform:
        if only_platform not in platforms:
            raise ValueError(f"平台 {only_platform} 不在 workspace.config.yaml 的 target_platforms 中")
        return [only_platform]
    return platforms


def process_platform(
    workspace_dir: Path,
    config: dict[str, Any],
    platform_rules: dict[str, dict[str, Any]],
    platform: str,
    creation_mode: str,
    *,
    force_images: bool,
    wechat_theme: str,
    dry_run: bool,
) -> dict[str, Any]:
    if platform not in platform_rules:
        raise ValueError(f"platform_styles_lib.json 中未定义平台: {platform}")

    workflow_route = platform_rules[platform].get("workflow_route", "long_form")
    delivery_mode = resolve_delivery_mode(config, platform)
    draft_file = resolve_draft_file(workspace_dir, platform)
    warnings: list[dict[str, Any]] = []

    print(f"\n=== 平台: {platform} | route={workflow_route} | delivery={delivery_mode} ===")
    print(f"  - draft: {draft_file}")

    src_images = list_source_images(workspace_dir)
    if not src_images:
        warnings.append(
            build_warning(
                platform,
                "source_images_empty",
                "Materials/Medias/images/ 未发现图片，继续执行后续步骤",
            )
        )
    copy_source_images(workspace_dir, platform, dry_run=dry_run)
    if workflow_route == "visual_first":
        image_plan = ensure_image_plan_output(workspace_dir, platform, dry_run=dry_run)
        if image_plan is None:
            warnings.append(
                build_warning(
                    platform,
                    "image_plan_missing",
                    f"未找到 Output/_drafts/03_image_plan.{platform}.md，已跳过 image_plan 同步",
                )
            )

    sanitize_article(
        workspace_dir,
        platform,
        workflow_route,
        draft_file,
        dry_run=dry_run,
    )

    run_illustration(
        workspace_dir,
        platform,
        force_images=force_images,
        dry_run=dry_run,
    )

    if platform == "wechat":
        html_output = run_markdown_to_wechat(workspace_dir, theme=wechat_theme, dry_run=dry_run)
    else:
        html_output = None

    publish_result = None
    if delivery_mode == "auto_format_and_publish":
        if platform not in PUBLISH_SUPPORTED_PLATFORMS:
            publish_result = {
                "status": "skipped",
                "message": f"{platform} 自动发布能力暂未接通，已跳过发布",
            }
            warnings.append(
                build_warning(
                    platform,
                    "publish_not_connected",
                    f"{platform} 自动发布能力暂未接通，当前仅完成本地交付包",
                )
            )
        else:
            publish_result = run_publisher(workspace_dir, platform, dry_run=dry_run)

    extra_outputs: list[str] = []
    if workflow_route == "visual_first":
        extra_outputs.append(f"image_plan：Output/{platform}/image_plan.md")
    metadata_path = workspace_dir / "Output" / platform / "metadata.yaml"
    if not metadata_path.exists():
        warnings.append(
            build_warning(
                platform,
                "metadata_missing",
                f"未找到 Output/{platform}/metadata.yaml，交付记录回写将被跳过",
            )
        )

    return {
        "platform": platform,
        "delivery_mode": delivery_mode,
        "workflow_route": workflow_route,
        "quality_score": resolve_quality_score(workspace_dir, platform),
        "article_rel": f"Output/{platform}/article.md",
        "images_rel": f"Output/{platform}/images/",
        "metadata_rel": f"Output/{platform}/metadata.yaml",
        "html_rel": f"Output/wechat/article.html" if html_output else None,
        "image_plan_rel": f"Output/{platform}/image_plan.md" if workflow_route == "visual_first" else None,
        "extra_outputs": extra_outputs,
        "publish_result": publish_result,
        "creation_mode": creation_mode,
        "warnings": warnings,
        "dry_run": dry_run,
    }


def main() -> None:
    args = parse_args()
    workspace_dir = Path(args.workspace).expanduser().resolve()
    if not workspace_dir.exists():
        raise SystemExit(f"工作区不存在: {workspace_dir}")

    config = load_workspace_config_yaml(str(workspace_dir))
    creation_mode = resolve_creation_mode(config)
    platform_rules = load_platform_rules()
    platforms = target_platforms(config, args.platform)
    if not platforms:
        raise SystemExit("workspace.config.yaml 未配置 target_platforms")
    print(f"=== Stage 6 creation.mode = {creation_mode} ===")

    summaries: list[dict[str, Any]] = []
    for platform in platforms:
        summary = process_platform(
            workspace_dir,
            config,
            platform_rules,
            platform,
            creation_mode,
            force_images=args.force_images,
            wechat_theme=args.wechat_theme,
            dry_run=args.dry_run,
        )
        write_delivery_record(workspace_dir, platform, summary, dry_run=args.dry_run)
        summaries.append(summary)

    write_workspace_delivery_summary(workspace_dir, summaries, dry_run=args.dry_run)
    write_autonomous_warning_report(
        workspace_dir,
        summaries,
        creation_mode=creation_mode,
        dry_run=args.dry_run,
    )

    for summary in summaries:
        render_platform_summary(summary)


if __name__ == "__main__":
    main()
