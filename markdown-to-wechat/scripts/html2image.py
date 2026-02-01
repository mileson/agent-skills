#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# 文件说明书 (File Manual)
## 核心功能 (Core Function)
将 HTML 文件转换为 PNG 长图，使用 Playwright 实现全页面截图

## 输入 (Input)
- HTML 文件路径
- 输出 PNG 文件路径
- 可选配置：视口宽度、截图质量等

## 输出 (Output)
- PNG 格式的长图文件
- 控制台输出转换状态信息

## 定位 (Position)
作为 markdown-to-wechat skill 的扩展功能，为用户提供 HTML 转图片能力

## 依赖 (Dependency)
- playwright - 浏览器自动化和截图核心库
- pathlib - 文件路径处理
- sys, argparse - 命令行参数解析

## 维护规则 (Maintenance Rules)
1. 每次修改代码逻辑后，必须检查并更新上述的【核心功能】、【输入】、【输出】等信息，确保文档与代码一致。
2. 禁止修改或删除本【维护规则】章节的内容。
3. 修改完成后，必须扫描当前文件所在的文件夹目录，找到对应的 [当前文件夹名称]_README.md 文档，并同步更新该 README 中关于本文件的描述信息。
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

def html_to_image(
    html_path: str,
    output_path: str,
    viewport_width: int = 700,
    full_page: bool = True,
    quality: int = 100,
    scale: str = "css",
    headless: bool = True,
    zoom_level: float = 2.0,
    top_padding: int = 80
) -> bool:
    """
    将 HTML 文件转换为 PNG 图片
    
    Args:
        html_path: HTML 文件路径
        output_path: 输出的 PNG 文件路径
        viewport_width: 视口宽度（像素），默认 700
        full_page: 是否截取全页面，默认 True
        quality: 图片质量（0-100），默认 100
        scale: 缩放类型，'css' 或 'device'，默认 'css'
        headless: 是否无头模式运行，默认 True
        zoom_level: 页面缩放倍数（默认 2.0 倍，适合移动端查看）
        top_padding: 顶部留白（像素），默认 80px，避免被设备刘海遮挡
    
    Returns:
        bool: 转换是否成功
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ 错误：未安装 Playwright")
        print("\n📦 安装步骤：")
        print("1. 安装 Python 包：pip install playwright")
        print("2. 安装浏览器引擎：playwright install chromium")
        print("\n💡 提示：首次安装会下载约 300MB 的浏览器引擎")
        return False
    
    # 验证输入文件
    html_file = Path(html_path)
    if not html_file.exists():
        print(f"❌ 错误：HTML 文件不存在: {html_path}")
        return False
    
    # 确保输出目录存在
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"\n🖼️  开始转换 HTML 到图片...")
    print(f"📄 输入文件: {html_file.name}")
    print(f"📏 视口宽度: {viewport_width}px")
    print(f"🎨 截图模式: {'全页面' if full_page else '视口内'}")
    
    try:
        with sync_playwright() as p:
            # 启动浏览器
            print("🚀 启动浏览器引擎...")
            browser = p.chromium.launch(headless=headless)
            
            # 创建页面并设置视口大小
            # device_scale_factor: 3 = 高清（3倍分辨率）, 4 = 超高清（4倍分辨率）
            context = browser.new_context(
                viewport={'width': viewport_width, 'height': 1080},
                device_scale_factor=3  # 3倍分辨率，平衡清晰度和文件大小
            )
            page = context.new_page()
            
            # 加载 HTML 文件
            print(f"📖 加载 HTML 文件...")
            file_url = f"file://{html_file.absolute()}"
            page.goto(file_url, wait_until="networkidle")
            
            # 等待字体加载（微信公众号文章通常使用自定义字体）
            page.wait_for_timeout(1000)
            
            # 应用顶部留白（避免被设备刘海遮挡）
            if top_padding > 0:
                print(f"📱 添加顶部安全区域: {top_padding}px...")
                page.evaluate(f"""
                    document.body.style.paddingTop = '{top_padding}px';
                """)
            
            # 应用 CSS zoom 放大页面（让内容看起来更大）
            if zoom_level != 1.0:
                print(f"🔍 应用 {zoom_level}x 缩放...")
                page.evaluate(f"""
                    document.body.style.zoom = '{zoom_level}';
                """)
                page.wait_for_timeout(500)  # 等待缩放生效
            
            # 截图
            print(f"📸 正在截图...")
            page.screenshot(
                path=str(output_file),
                full_page=full_page,
                type="png",
                scale=scale,
                animations="disabled"  # 禁用动画确保一致性
            )
            
            # 关闭浏览器
            browser.close()
            
            # 获取文件大小
            file_size = output_file.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            
            print(f"\n✅ 转换成功！")
            print(f"💾 输出文件: {output_file.absolute()}")
            print(f"📦 文件大小: {file_size_mb:.2f} MB")
            
            return True
            
    except Exception as e:
        print(f"\n❌ 转换失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="将 HTML 文件转换为 PNG 长图",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 基本用法
  python html2image.py input.html output.png
  
  # 指定视口宽度为 1200px
  python html2image.py input.html output.png --width 1200
  
  # 仅截取视口内容（不截取全页面）
  python html2image.py input.html output.png --no-full-page
  
  # 设置图片质量为 90
  python html2image.py input.html output.png --quality 90
        """
    )
    
    parser.add_argument(
        "html_path",
        help="输入的 HTML 文件路径"
    )
    
    parser.add_argument(
        "output_path",
        help="输出的 PNG 文件路径"
    )
    
    parser.add_argument(
        "-w", "--width",
        type=int,
        default=800,
        help="视口宽度（像素），默认 800"
    )
    
    parser.add_argument(
        "--no-full-page",
        action="store_true",
        help="仅截取视口内容，不截取全页面"
    )
    
    parser.add_argument(
        "-q", "--quality",
        type=int,
        default=100,
        choices=range(1, 101),
        metavar="[1-100]",
        help="图片质量（1-100），默认 100"
    )
    
    parser.add_argument(
        "--scale",
        choices=["css", "device"],
        default="css",
        help="缩放类型，默认 'css'"
    )
    
    parser.add_argument(
        "--show-browser",
        action="store_true",
        help="显示浏览器窗口（调试用）"
    )
    
    args = parser.parse_args()
    
    # 执行转换
    success = html_to_image(
        html_path=args.html_path,
        output_path=args.output_path,
        viewport_width=args.width,
        full_page=not args.no_full_page,
        quality=args.quality,
        scale=args.scale,
        headless=not args.show_browser
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
