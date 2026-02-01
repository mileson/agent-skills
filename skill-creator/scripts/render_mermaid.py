#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mermaid 图表渲染脚本 - Skill Creator 专用

将 Mermaid 代码渲染为 PNG 图片并自动打开预览。
使用在线 API 渲染，无需本地安装 Chrome/Puppeteer。

依赖: Python 3.6+
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
import urllib.request
import base64
import zlib

# 默认输出目录
DEFAULT_OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "mermaid-imgs"
)


def create_no_proxy_opener():
    """创建绕过系统代理的 opener"""
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def render_with_kroki(mermaid_code: str, output_path: str) -> bool:
    """
    使用 Kroki API 渲染 Mermaid 图表 (支持中文)

    Kroki 使用 deflate + base64 编码，正确处理 UTF-8 中文字符。
    编码算法: UTF-8 bytes → zlib.compress(level 9) → URL-safe base64

    Args:
        mermaid_code: Mermaid 图表代码
        output_path: 输出 PNG 文件路径

    Returns:
        成功返回 True，失败返回 False
    """
    try:
        # Kroki 编码: UTF-8 → deflate (level 9) → URL-safe base64
        compressed = zlib.compress(mermaid_code.encode('utf-8'), 9)
        encoded = base64.urlsafe_b64encode(compressed).decode().rstrip('=')
        url = f"https://kroki.io/mermaid/png/{encoded}"

        opener = create_no_proxy_opener()
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')

        with opener.open(request, timeout=30) as response:
            with open(output_path, 'wb') as f:
                f.write(response.read())

        return True

    except Exception as e:
        print(f"Kroki 渲染失败: {e}", file=sys.stderr)
        return False


def render_with_mermaidink(mermaid_code: str, output_path: str) -> bool:
    """
    使用 mermaid.ink 在线 API 渲染 Mermaid 图表

    Args:
        mermaid_code: Mermaid 图表代码
        output_path: 输出 PNG 文件路径

    Returns:
        成功返回 True，失败返回 False
    """
    try:
        # 使用标准 base64 编码
        encoded = base64.b64encode(mermaid_code.encode('utf-8')).decode()
        url = f"https://mermaid.ink/img/{encoded}?type=png"

        # 使用无代理 opener
        opener = create_no_proxy_opener()
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')

        # 下载图片
        with opener.open(request, timeout=30) as response:
            with open(output_path, 'wb') as f:
                f.write(response.read())

        return True

    except Exception as e:
        print(f"mermaid.ink PNG 渲染失败: {e}", file=sys.stderr)
        return False


def render_with_mermaidink_svg(mermaid_code: str, output_path: str) -> bool:
    """
    使用 mermaid.ink 渲染为 SVG（备用方案）

    Args:
        mermaid_code: Mermaid 图表代码
        output_path: 输出文件路径

    Returns:
        成功返回 True，失败返回 False
    """
    try:
        # 下载 SVG
        encoded = base64.b64encode(mermaid_code.encode('utf-8')).decode()
        url = f"https://mermaid.ink/svg/{encoded}"

        opener = create_no_proxy_opener()
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')

        # 获取 SVG
        with opener.open(request, timeout=30) as response:
            svg_data = response.read().decode('utf-8')

        # 保存为 SVG 文件
        svg_path = output_path.rsplit('.', 1)[0] + '.svg'
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_data)

        # 尝试使用 macOS 的 qlmanage 将 SVG 转为 PNG
        try:
            result = subprocess.run([
                'qlmanage', '-t', '-s', '1000', '-o',
                os.path.dirname(output_path) or '.',
                svg_path
            ], capture_output=True, timeout=10)

            # qlmanage 生成 .png 文件，重命名
            ql_png = svg_path.rsplit('.', 1)[0] + '.png'
            if os.path.exists(ql_png):
                os.rename(ql_png, output_path)
                return True
        except:
            pass

        # 如果转换失败，至少返回 SVG 路径
        print(f"⚠️ PNG 转换失败，已生成 SVG: {svg_path}", file=sys.stderr)
        if sys.platform == "darwin":
            subprocess.run(["open", svg_path])
        return True

    except Exception as e:
        print(f"mermaid.ink SVG 渲染失败: {e}", file=sys.stderr)
        return False


def open_preview(file_path: str) -> None:
    """打开图片预览"""
    try:
        if sys.platform == "darwin":
            subprocess.run(["open", file_path])
        elif sys.platform.startswith("linux"):
            subprocess.run(["xdg-open", file_path])
        elif sys.platform == "win32":
            os.startfile(file_path)
    except Exception as e:
        print(f"无法打开预览: {e}", file=sys.stderr)


def render_mermaid(
    mermaid_code: str,
    output_path: str = None,
    auto_open: bool = True,
    output_dir: str = None
) -> str:
    """
    渲染 Mermaid 代码为 PNG 图片

    Args:
        mermaid_code: Mermaid 图表代码
        output_path: 输出文件路径，默认为时间戳文件名
        auto_open: 是否自动打开预览
        output_dir: 输出目录，默认为 skill-creator/mermaid-imgs/

    Returns:
        生成的图片文件路径
    """
    # 确定输出目录
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 确定输出路径
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"skill-plan-{timestamp}.png")

    output_path = os.path.expanduser(output_path)
    output_path = os.path.abspath(output_path)

    # 方案 1: Kroki API (支持中文)
    print("正在使用 Kroki API 渲染 (支持中文)...", file=sys.stderr)
    if render_with_kroki(mermaid_code, output_path):
        print(f"✓ Mermaid 图表已生成: {output_path}")

        if auto_open:
            open_preview(output_path)

        return output_path

    # 备用方案 2: mermaid.ink PNG
    print("尝试备用渲染方式 (mermaid.ink PNG)...", file=sys.stderr)
    if render_with_mermaidink(mermaid_code, output_path):
        print(f"✓ Mermaid 图表已生成: {output_path}")

        if auto_open:
            open_preview(output_path)

        return output_path

    # 备用方案 3: mermaid.ink SVG
    print("尝试备用渲染方式 (mermaid.ink SVG)...", file=sys.stderr)
    if render_with_mermaidink_svg(mermaid_code, output_path):
        svg_path = output_path.rsplit('.', 1)[0] + '.svg'
        if os.path.exists(output_path):
            print(f"✓ Mermaid 图表已生成: {output_path}")
        else:
            output_path = svg_path
            print(f"✓ Mermaid 图表已生成 (SVG): {output_path}")

        if auto_open:
            open_preview(output_path)

        return output_path

    print("所有渲染方式均失败，请检查网络连接", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="渲染 Mermaid 图表为 PNG 图片并打开预览 (Skill Creator 专用)"
    )
    parser.add_argument(
        "-c", "--code",
        help="Mermaid 代码（内联）"
    )
    parser.add_argument(
        "-f", "--file",
        help="包含 Mermaid 代码的文件路径"
    )
    parser.add_argument(
        "-o", "--output",
        help="输出文件路径（默认: skill-plan-TIMESTAMP.png）"
    )
    parser.add_argument(
        "-d", "--output-dir",
        help=f"输出目录（默认: {DEFAULT_OUTPUT_DIR}）"
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="不自动打开预览"
    )

    args = parser.parse_args()

    # 获取 Mermaid 代码
    if args.code:
        mermaid_code = args.code
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            mermaid_code = f.read()
    else:
        # 从 stdin 读取
        mermaid_code = sys.stdin.read()

    if not mermaid_code.strip():
        print("错误: 未提供 Mermaid 代码", file=sys.stderr)
        sys.exit(1)

    # 渲染
    render_mermaid(
        mermaid_code,
        output_path=args.output,
        auto_open=not args.no_open,
        output_dir=args.output_dir
    )


if __name__ == "__main__":
    main()
