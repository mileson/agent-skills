#!/usr/bin/env python3
"""
AI 封面图生成工具

通过 secrets-vault 中的 apimart_image 配置调用 Gemini 图像生成 API，
自动生成文章封面图并保存到指定路径。

两种模式：
  默认模式（推荐）：传入 --article 文章路径，自动使用内置「科技视觉绘图专家」提示词模板
  自定义模式：传入 --prompt 自定义描述

输出路径：
  --workspace 自动保存到 Materials/Medias/images/cover.jpg（推荐）
  --output 直接指定输出路径

Usage:
    # 默认模式：读取文章内容 + 内置提示词模板（推荐）
    python3 generate_cover.py --article /path/to/article.md --workspace /path/to/workspace

    # 自定义模式：直接指定 prompt
    python3 generate_cover.py --prompt "自定义描述" --workspace /path/to/workspace

    # 指定输出路径（替代 --workspace）
    python3 generate_cover.py --article /path/to/article.md --output /path/to/cover.jpg

    # 可选参数
    --size 16:9          # 图片比例（默认 16:9）
    --resolution 1K      # 分辨率: 1K/2K/4K（默认 1K）
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


# ═══════════════════════════════════════════════════════════════════════
# 内置提示词模板：科技视觉绘图专家 (Tech Visual Illustrator)
# 当使用 --article 模式时，{article_content} 会被替换为文章内容
# ═══════════════════════════════════════════════════════════════════════

DEFAULT_PROMPT_TEMPLATE = r"""
# 科技视觉绘图专家 (Tech Visual Illustrator)


## 角色设定（Role Definition）
你是一位专精于科技媒体头图设计的资深视觉总监，拥有好莱坞级别的宽幅构图审美。你深谙微信公众号（WeChat Official Account）的视觉传播法则，擅长在 16:9 的宽阔画幅中，利用"暗黑赛博"与"光影折射"构建具有叙事张力的 3D 场景。你的核心能力在于视觉转译——能敏锐抓取文章或链接中的核心论点，将其瞬间转化为极具点击欲望的、电影级质感的超写实渲染图，确保在信息流中一眼抓住读者眼球。


## 核心任务（Core Task）
你的任务是接收用户的内容（链接或文本），直接调用绘图工具生成符合特定"暗黑科技/赛博朋克"风格的封面图。


## 核心工作流 (Core Workflow)
当用户提供输入后，你必须严格按以下步骤执行，不要询问，直接行动：
1. 分析内容 (Analyze):
- 若为链接：必须联网深度阅读，提炼核心主题。
- 若为文本：理解核心语义。

2. 设计画面 (Design): 在后台构建视觉隐喻，将抽象概念转化为具象的 3D 物体（如：玻璃质感的芯片、发光的锁链、全息投影）。

3. 执行绘图 (EXECUTE DRAWING):
- 立即调用你的绘图工具 (DALL-E / Image Gen Tool)。
- 不要仅仅输出文字描述，必须直接生成图片。


## 视觉风格规范 (Strict Style Protocol)
你构建给绘图工具的 Prompt 必须强制包含以下风格元素（你自己在后台组合，无需展示给用户）：
- 基础画质: 3D Render, Octane Render (OC渲染), Unreal Engine 5, Hyper-realistic (超写实), 8k resolution.
- 色调: Dark Mode (暗黑模式), Deep Navy Background (深蓝/黑背景). 点缀色：Neon Cyan (青), Electric Violet (紫), Gold (金).
- 光影: Volumetric lighting (体积光), Glowing edges (边缘发光), Glassmorphism (玻璃拟态), Metallic textures (金属质感).
- 氛围: Cyberpunk (赛博朋克), Data flow (数据流), High-tech abstract (高科技抽象).
- 构图: Wide angle (广角), Center composition (主体居中但留白).
- 文字: 【最高优先级规则】图像中如果出现任何文字、标签、标注、数字标识、UI元素上的文字，必须全部使用中文（简体中文）。严禁出现任何英文字母、英文单词或英文句子。如果无法确保文字是中文，则不要在图像中放入任何文字。
- 其他元素：如果用户提供了附图的元素，请将认真分析这些图像，并将其完美地融入到生成的图像中.


## 尺寸设置 (Aspect Ratio)
- 强制比例: 设置绘图工具生成的图片比例为 Wide (16:9) 或尽量接近 2.35:1 (取决于具体工具支持的最宽比例)，以适配微信公众号封面。


## 示例逻辑 (Internal Logic Example)
- 场景:用户输入关于"AI 隐私泄露"。
- 你的行动: 立即生成图像，提示词包含："High-tech 3D render of a cracked glass padlock floating in a dark digital void, data leaking out like liquid neon, cyberpunk city background, octane render, dark blue aesthetic, [User-specified aspect ratio] aspect ratio." -> [生成图片]


## 用户输入的内容 (User Configuration)
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
                      size: str = "16:9", resolution: str = "1K") -> str:
    """提交图像生成任务，返回 task_id"""
    data = _curl_json("POST", api_url, api_token, {
        "model": model,
        "prompt": prompt,
        "size": size,
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

def build_prompt_from_article(article_path: str, lang: str = "zh") -> str:
    """读取文章内容，注入内置「科技视觉绘图专家」模板。

    模板已包含：
    - 暗黑赛博/3D 渲染风格约束
    - 强制图片中文字使用中文（默认）或英文
    - 16:9 宽幅构图
    - 视觉转译工作流
    """
    with open(article_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 文章过长时截断，保留核心内容（标题 + 前部分）以避免超出模型 token 限制
    max_chars = 6000
    if len(content) > max_chars:
        content = content[:max_chars] + "\n\n[... 内容已截断，以上为核心部分 ...]"

    prompt = DEFAULT_PROMPT_TEMPLATE.replace("{article_content}", content)

    # 在最终 prompt 头部再追加一层语言强制约束（双重保险）
    if lang == "zh":
        lang_guard = (
            "【最高优先级指令 - 必须遵守】"
            "生成的图像中，所有可见文字、标签、数字标识、UI文字必须使用中文（简体中文）。"
            "严禁出现任何英文字母或英文单词。"
            "如果无法保证文字是中文，就不要在图像中放任何文字。\n\n"
        )
    else:
        lang_guard = ""

    return lang_guard + prompt


def build_prompt_custom(user_prompt: str, lang: str = "zh") -> str:
    """为自定义 prompt 添加语言和质量约束。

    默认生成中文内容的图片（lang=zh），
    仅当用户明确要求英文时传 lang=en。
    """
    quality_suffix = (
        "Professional quality, high resolution, clean composition, "
        "suitable for article cover image."
    )
    if lang == "zh":
        lang_prefix = (
            "【重要】图片中出现的所有文字、标签、标注、说明必须使用中文（简体）。"
            "不要出现任何英文文字。"
        )
        return f"{lang_prefix} {user_prompt} {quality_suffix}"
    else:
        return f"{user_prompt} {quality_suffix}"


def resolve_output_path(args) -> str:
    """根据参数解析输出路径。

    优先级：
    1. --output 直接指定路径
    2. --workspace 自动保存到 Materials/Medias/images/cover.jpg
    """
    if args.output:
        return args.output
    if args.workspace:
        return os.path.join(args.workspace, "Materials", "Medias", "images", "cover.jpg")
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
  # 默认模式（推荐）：读取文章，使用内置「科技视觉绘图专家」提示词
  python3 generate_cover.py --article Output/wechat/article.md --workspace .

  # 自定义模式：直接描述
  python3 generate_cover.py --prompt "深蓝色背景的AI芯片封面" --workspace .
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

    # 输出路径：二选一
    output_group = parser.add_mutually_exclusive_group(required=True)
    output_group.add_argument(
        "--output",
        help="直接指定输出文件路径",
    )
    output_group.add_argument(
        "--workspace",
        help="工作区根目录，自动保存到 Materials/Medias/images/cover.jpg",
    )

    parser.add_argument(
        "--size", default="16:9",
        help="图片比例 (默认 16:9，支持: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9)",
    )
    parser.add_argument(
        "--resolution", default="1K",
        help="分辨率: 1K/2K/4K (默认 1K)",
    )
    parser.add_argument(
        "--lang", default="zh", choices=["zh", "en"],
        help="自定义模式下图片中文字的语言 (默认 zh 中文，--article 模式下忽略此参数)",
    )
    args = parser.parse_args()

    # ── 解析输出路径 ──
    output_path = resolve_output_path(args)

    # ── 构建最终 prompt ──
    if args.article:
        if not os.path.isfile(args.article):
            print(f"❌ 文件不存在: {args.article}")
            sys.exit(1)
        mode = "article"
        final_prompt = build_prompt_from_article(args.article, args.lang)
        display_source = os.path.basename(args.article)
    else:
        mode = "custom"
        final_prompt = build_prompt_custom(args.prompt, args.lang)
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
    print(f"   来源: {display_source}")
    print(f"   输出: {output_path}")
    print(f"   比例: {args.size} | 分辨率: {args.resolution}")
    task_id = submit_image_task(api_url, api_token, model, final_prompt, args.size, args.resolution)
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
