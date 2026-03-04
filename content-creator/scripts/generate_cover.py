#!/usr/bin/env python3
"""
AI 封面图生成工具

通过 secrets-vault 中的 apimart_image 配置调用 Gemini 图像生成 API，
自动生成文章封面图并保存到指定路径。

两种模式：
  默认模式（推荐）：传入 --article 文章路径，自动使用内置平台封面提示词模板
  自定义模式：传入 --prompt 自定义描述

输出路径：
  --workspace 自动保存到 Materials/Medias/images/cover-{platform}.jpg（推荐）
  --output 直接指定输出路径

Usage:
    # 默认模式：读取文章内容 + 平台预设（推荐）
    python3 generate_cover.py --article /path/to/article.md --platform wechat --workspace /path/to/workspace

    # 自定义模式：直接指定 prompt
    python3 generate_cover.py --prompt "自定义描述" --platform twitter --workspace /path/to/workspace

    # 指定输出路径（替代 --workspace）
    python3 generate_cover.py --article /path/to/article.md --platform jike --output /path/to/cover.jpg

    # 可选参数
    --aspect_ratio 21:9  # 图片横纵比（默认取平台 preset，--size 为兼容别名）
    --resolution 1K      # 分辨率: 1K/2K/4K（默认 1K，除非用户明确要求更高清再调整）
    --lang en            # 自定义模式下生成英文内容（默认 zh 中文）

Requires:
    - secrets-vault skill 已配置 apimart_image 命名空间
"""

import argparse
import json
import os
import subprocess
import sys
import time

SUPPORTED_ASPECT_RATIOS = [
    "1:1", "3:2", "2:3", "4:3", "3:4",
    "16:9", "9:16", "5:4", "4:5", "21:9",
    "1:4", "4:1", "1:8", "8:1"
]

PLATFORM_PRESETS = {
    "wechat": {
        "display_name": "微信公众号",
        "default_aspect_ratio": "21:9",
        "recommended_size": "900x383",
        "visual_direction": "科技媒体头图、宽幅编辑感、电影级首屏视觉",
        "composition_rule": "主体聚焦中央安全区，左右保留叙事空间，适合横向封面裁切",
        "feed_goal": "在文章列表和分享卡片里一眼抓住读者注意力",
    },
    "jike": {
        "display_name": "即刻",
        "default_aspect_ratio": "1:1",
        "recommended_size": "1080x1080",
        "visual_direction": "极简科技社区、清爽留白、信息密度高但不拥挤",
        "composition_rule": "主体居中，四周留足安全边距，适合小尺寸方图预览",
        "feed_goal": "在社区动态流中保持辨识度，同时不破坏即刻的轻量感",
    },
    "twitter": {
        "display_name": "Twitter/X",
        "default_aspect_ratio": "4:5",
        "recommended_size": "1440x1800",
        "visual_direction": "高冲击视觉海报、移动端优先、强主体和高对比",
        "composition_rule": "纵向卡片构图，主体位于中上区域，适合 feed 首图停留",
        "feed_goal": "在移动端时间线中提升停留和点击意愿",
    },
    "xhs": {
        "display_name": "小红书",
        "default_aspect_ratio": "3:4",
        "recommended_size": "1080x1440",
        "visual_direction": "封面感、生活化、强视觉主题，适合图文笔记首图",
        "composition_rule": "竖版构图，主体偏中上，预留封面标题安全区",
        "feed_goal": "适合作为图文笔记封面，但当前仅预留未来接入",
    },
    "zhihu": {
        "display_name": "知乎",
        "default_aspect_ratio": "16:9",
        "recommended_size": "1280x720",
        "visual_direction": "知识型头图、克制、理性、主题清晰",
        "composition_rule": "宽幅横图，主体居中，强调概念表达和信息整洁",
        "feed_goal": "适合作为文章头图，但当前仅预留未来接入",
    },
}


# ═══════════════════════════════════════════════════════════════════════
# 内置提示词模板：平台封面图生成器
# 当使用 --article 模式时，{article_content} 会被替换为文章内容
# ═══════════════════════════════════════════════════════════════════════

DEFAULT_PROMPT_TEMPLATE = r"""
# 平台封面图生成器 (Platform Cover Illustrator)

## 角色设定（Role Definition）
你是一位擅长将文章核心论点转译为封面图的资深视觉总监。你需要根据目标平台的展示方式，
生成一张适合 {platform_display_name} 内容首屏传播的 AI 封面图。

## 平台约束（Platform Context）
- 目标平台：{platform_display_name}
- 推荐尺寸：{recommended_size}
- 推荐比例：{aspect_ratio}
- 视觉方向：{visual_direction}
- 构图规则：{composition_rule}
- 传播目标：{feed_goal}

## 核心任务（Core Task）
阅读文章内容，提炼核心论点、情绪和视觉隐喻，生成一张具有传播力的科技主题封面图。

## 视觉规范（Strict Style Protocol）
- 基础画质：high detail, cinematic lighting, editorial composition, hyper-realistic or premium concept illustration
- 风格基调：现代科技、电影感、强叙事、避免廉价模板感
- 构图要求：严格遵循目标平台比例，主体保持在中央安全区
- 文字要求：默认不要在图片中渲染任何可见文字、数字、UI 标签、水印或 logo
- 内容要求：不要生成信息图，不要生成带大段文案的海报，不要生成 low-res 或拥挤拼贴

## 用户输入的内容（User Configuration）
{article_content}
""".strip()


# ═══════════════════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════════════════

def get_secret(namespace: str, key: str = None) -> str:
    """从 secrets-vault 获取凭证"""
    script = os.path.expanduser("~/.cursor/skills/secrets-vault/scripts/get_secret.py")
    cmd = ["python3", script, namespace]
    if key:
        cmd.append(key)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to get secret: {result.stderr.strip()}")
    return result.stdout.strip()


def _curl_json(method: str, url: str, token: str, payload: dict = None,
               retries: int = 3) -> dict:
    """使用 curl 发起 HTTP 请求（避免 macOS Python SSL 证书问题）。

    自带重试机制：遇到空响应或网络错误时自动重试。
    """
    cmd = ["curl", "-s", "--connect-timeout", "15", "--max-time", "30",
           "--request", method, "--url", url,
           "--header", f"Authorization: Bearer {token}"]
    if payload:
        cmd += ["--header", "Content-Type: application/json",
                "--data", json.dumps(payload)]

    last_error = None
    for attempt in range(retries):
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            last_error = RuntimeError(f"curl failed (attempt {attempt+1}): {result.stderr}")
            time.sleep(2)
            continue
        raw = result.stdout.strip()
        if not raw:
            last_error = RuntimeError(f"Empty response (attempt {attempt+1})")
            time.sleep(2)
            continue
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            last_error = RuntimeError(f"JSON decode error (attempt {attempt+1}): {e} | raw: {raw[:200]}")
            time.sleep(2)
            continue

    raise last_error


def submit_image_task(api_url: str, api_token: str, model: str, prompt: str,
                      aspect_ratio: str = "16:9", resolution: str = "1K") -> str:
    """提交图像生成任务，返回 task_id"""
    data = _curl_json("POST", api_url, api_token, {
        "model": model,
        "prompt": prompt,
        "size": aspect_ratio,
        "n": 1,
        "resolution": resolution,
    })

    if data.get("code") != 200:
        raise RuntimeError(f"API error: {json.dumps(data, ensure_ascii=False)}")

    return data["data"][0]["task_id"]


def poll_task(task_status_url: str, api_token: str, task_id: str,
              max_wait: int = 180, interval: int = 3) -> str:
    """轮询任务状态，返回图片 URL"""
    url = f"{task_status_url}/{task_id}"

    elapsed = 0
    while elapsed < max_wait:
        data = _curl_json("GET", url, api_token)
        status = data.get("data", {}).get("status", "")

        if status == "completed":
            images = data["data"].get("result", {}).get("images", [])
            if images and images[0].get("url"):
                return images[0]["url"][0]
            raise RuntimeError("Task completed but no image URL found")

        if status == "failed":
            error = data.get("data", {}).get("error", {})
            raise RuntimeError(f"Task failed: {error.get('message', 'unknown error')}")

        time.sleep(interval)
        elapsed += interval

    raise TimeoutError(f"Task {task_id} did not complete within {max_wait}s")


def download_image(image_url: str, output_path: str):
    """下载图片到本地"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result = subprocess.run(
        ["curl", "-sL", image_url, "-o", output_path],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Download failed: {result.stderr}")


# ═══════════════════════════════════════════════════════════════════════
# Prompt 构建
# ═══════════════════════════════════════════════════════════════════════

def get_platform_preset(platform: str | None) -> dict:
    """返回平台 preset；未指定则使用通用默认值。"""
    if platform and platform in PLATFORM_PRESETS:
        return PLATFORM_PRESETS[platform]
    return {
        "display_name": "通用平台",
        "default_aspect_ratio": "16:9",
        "recommended_size": "1280x720",
        "visual_direction": "现代科技媒体封面，强调主题提炼和视觉记忆点",
        "composition_rule": "主体保持在中央安全区，避免贴边和复杂拼贴",
        "feed_goal": "提升内容首屏点击意愿",
    }


def build_prompt_from_article(
    article_path: str,
    platform: str | None = None,
    lang: str = "zh",
    aspect_ratio: str = "16:9"
) -> str:
    """读取文章内容，注入平台封面模板。"""
    with open(article_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 文章过长时截断，保留核心内容（标题 + 前部分）以避免超出模型 token 限制
    max_chars = 6000
    if len(content) > max_chars:
        content = content[:max_chars] + "\n\n[... 内容已截断，以上为核心部分 ...]"

    preset = get_platform_preset(platform)
    prompt = DEFAULT_PROMPT_TEMPLATE.format(
        platform_display_name=preset["display_name"],
        recommended_size=preset["recommended_size"],
        aspect_ratio=aspect_ratio,
        visual_direction=preset["visual_direction"],
        composition_rule=preset["composition_rule"],
        feed_goal=preset["feed_goal"],
        article_content=content,
    )

    text_guard = (
        "【最高优先级指令】不要在图片中渲染任何可见文字、数字、UI 标签、水印或 logo。"
        "只输出纯画面封面，不做信息海报。\n\n"
    )

    return text_guard + prompt


def build_prompt_custom(
    user_prompt: str,
    lang: str = "zh",
    aspect_ratio: str = "16:9",
    platform: str | None = None
) -> str:
    """为自定义 prompt 添加语言和质量约束。

    默认生成中文内容的图片（lang=zh），
    仅当用户明确要求英文时传 lang=en。
    """
    preset = get_platform_preset(platform)
    quality_suffix = (
        "Professional quality, high resolution, clean composition, "
        f"suitable for {preset['display_name']} article cover image. "
        f"Recommended canvas {preset['recommended_size']}."
    )
    if lang == "zh":
        lang_prefix = (
            "【重要】图片中出现的所有文字、标签、标注、说明必须使用中文（简体）。"
            "不要出现任何英文文字。"
        )
        return f"{lang_prefix} Aspect ratio: {aspect_ratio}. {user_prompt} {quality_suffix}"
    else:
        return f"Aspect ratio: {aspect_ratio}. {user_prompt} {quality_suffix}"


def resolve_output_path(args) -> str:
    """根据参数解析输出路径。

    优先级：
    1. --output 直接指定路径
    2. --workspace 自动保存到 Materials/Medias/images/cover-{platform}.jpg
    """
    if args.output:
        return args.output
    if args.workspace:
        filename = "cover.jpg"
        if getattr(args, "platform", None):
            filename = f"cover-{args.platform}.jpg"
        return os.path.join(args.workspace, "Materials", "Medias", "images", filename)
    raise ValueError("必须指定 --output 或 --workspace 其中之一")


# ═══════════════════════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="AI 封面图生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 默认模式（推荐）：读取文章，使用平台预设
  python3 generate_cover.py --article Output/wechat/article.md --platform wechat --workspace .

  # 自定义模式：直接描述
  python3 generate_cover.py --prompt "深蓝色背景的AI芯片封面" --platform twitter --workspace .
""",
    )

    # Prompt 来源：二选一
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument(
        "--article",
        help="文章 Markdown 文件路径（使用内置「科技视觉绘图专家」模板，推荐）",
    )
    prompt_group.add_argument(
        "--prompt",
        help="自定义图片描述 prompt",
    )

    parser.add_argument(
        "--platform",
        choices=sorted(PLATFORM_PRESETS.keys()),
        help="目标平台，决定默认比例、视觉方向和默认输出文件名",
    )

    # 输出路径：二选一
    output_group = parser.add_mutually_exclusive_group(required=True)
    output_group.add_argument(
        "--output",
        help="直接指定输出文件路径",
    )
    output_group.add_argument(
        "--workspace",
        help="工作区根目录，自动保存到 Materials/Medias/images/cover-{platform}.jpg",
    )

    parser.add_argument(
        "--aspect_ratio", "--size",
        dest="aspect_ratio",
        default=None,
        choices=SUPPORTED_ASPECT_RATIOS,
        help="图片横纵比 (默认取平台 preset；未指定平台时为 16:9；--size 为兼容别名)",
    )
    parser.add_argument(
        "--resolution", default="1K",
        help="分辨率: 1K/2K/4K (默认 1K，除非用户明确要求更高清再调整)",
    )
    parser.add_argument(
        "--lang", default="zh", choices=["zh", "en"],
        help="自定义模式下图片中文字的语言 (默认 zh 中文，--article 模式下忽略此参数)",
    )
    args = parser.parse_args()

    # ── 解析输出路径 ──
    output_path = resolve_output_path(args)

    # ── 构建最终 prompt ──
    aspect_ratio = args.aspect_ratio
    if aspect_ratio is None:
        aspect_ratio = get_platform_preset(args.platform)["default_aspect_ratio"]

    if args.article:
        if not os.path.isfile(args.article):
            print(f"❌ 文件不存在: {args.article}")
            sys.exit(1)
        mode = "article"
        final_prompt = build_prompt_from_article(args.article, args.platform, args.lang, aspect_ratio)
        display_source = os.path.basename(args.article)
    else:
        mode = "custom"
        final_prompt = build_prompt_custom(args.prompt, args.lang, aspect_ratio, args.platform)
        display_source = args.prompt[:80]

    # ── 1. 从 secrets-vault 获取 API 配置 ──
    print("🔑 读取 API 配置...")
    api_url = get_secret("apimart_image", "api_url")
    api_token = get_secret("apimart_image", "api_token")
    model = get_secret("apimart_image", "model")
    task_status_url = get_secret("apimart_image", "task_status_url")

    # ── 2. 提交生成任务 ──
    print(f"🎨 提交图像生成任务...")
    print(f"   模式: {'内置模板 + 文章内容' if mode == 'article' else '自定义 prompt'}")
    print(f"   平台: {args.platform or 'generic'}")
    print(f"   来源: {display_source}")
    print(f"   输出: {output_path}")
    print(f"   横纵比: {aspect_ratio} | 分辨率: {args.resolution}")
    task_id = submit_image_task(api_url, api_token, model, final_prompt, aspect_ratio, args.resolution)
    print(f"   Task ID: {task_id}")

    # ── 3. 轮询等待 ──
    print("⏳ 等待生成完成...")
    image_url = poll_task(task_status_url, api_token, task_id)
    print(f"   ✅ 生成完成")

    # ── 4. 下载图片 ──
    print(f"📥 下载图片到 {output_path}...")
    download_image(image_url, output_path)
    file_size = os.path.getsize(output_path)
    print(f"   ✅ 保存成功 ({file_size / 1024:.0f} KB)")

    # ── 5. 输出 JSON 结果 ──
    result = {
        "status": "success",
        "mode": mode,
        "task_id": task_id,
        "image_url": image_url,
        "output_path": output_path,
        "file_size": file_size,
    }
    print(f"\n{'='*50}")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
