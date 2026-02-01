#!/usr/bin/env python3
"""
Workspace Detector - 工作区结构检测器

功能：
1. 检测 Output/ 目录结构
2. 查找各平台的 article.md
3. 返回 JSON 结果供 AI 决策

使用：
    python detect_workspace.py [directory]

返回格式：
{
  "workspace_type": "content_creator" | "standalone" | "unknown",
  "output_exists": true,
  "platforms": [
    {
      "name": "wechat",
      "path": "Output/wechat",
      "article_exists": true,
      "article_path": "Output/wechat/article.md",
      "images_exists": true,
      "images_path": "Output/wechat/images",
      "image_count": 5
    }
  ],
  "recommendation": {
    "action": "auto_select" | "ask_user" | "no_article",
    "target": "Output/wechat/article.md" | null,
    "message": "自动选择唯一的文章..."
  }
}
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any


def detect_workspace(directory: Path = None) -> Dict[str, Any]:
    """
    检测工作区结构
    
    Args:
        directory: 工作区目录（默认当前目录）
    
    Returns:
        检测结果字典
    """
    if directory is None:
        directory = Path.cwd()
    else:
        directory = Path(directory)
    
    result = {
        "workspace_root": str(directory.absolute()),
        "workspace_type": "unknown",
        "output_exists": False,
        "platforms": [],
        "recommendation": {
            "action": "no_article",
            "target": None,
            "message": "未找到 Output/ 目录或 article.md 文件"
        }
    }
    
    # 检查 Output/ 目录
    output_dir = directory / "Output"
    
    if not output_dir.exists():
        # 没有 Output 目录，检查当前目录是否有 .md 文件
        md_files = list(directory.glob("*.md"))
        if md_files:
            result["workspace_type"] = "standalone"
            result["recommendation"] = {
                "action": "ask_user",
                "target": None,
                "message": f"当前目录有 {len(md_files)} 个 Markdown 文件，请指定要转换的文件"
            }
        return result
    
    result["output_exists"] = True
    result["workspace_type"] = "content_creator"
    
    # 支持的平台列表
    supported_platforms = [
        "wechat",      # 微信公众号
        "xhs",         # 小红书
        "zhihu",       # 知乎
        "jike",        # 即刻
        "douyin",      # 抖音
        "bilibili",    # B站
    ]
    
    # 扫描各平台目录
    for platform in supported_platforms:
        platform_dir = output_dir / platform
        
        if not platform_dir.exists():
            continue
        
        platform_info = {
            "name": platform,
            "path": str(platform_dir.relative_to(directory)),
            "article_exists": False,
            "article_path": None,
            "images_exists": False,
            "images_path": None,
            "image_count": 0
        }
        
        # 检查 article.md
        article_file = platform_dir / "article.md"
        if article_file.exists():
            platform_info["article_exists"] = True
            platform_info["article_path"] = str(article_file.relative_to(directory))
        
        # 检查 images/ 目录
        images_dir = platform_dir / "images"
        if images_dir.exists():
            platform_info["images_exists"] = True
            platform_info["images_path"] = str(images_dir.relative_to(directory))
            
            # 统计图片数量
            image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
            image_files = []
            for ext in image_extensions:
                image_files.extend(images_dir.glob(f"*{ext}"))
            platform_info["image_count"] = len(image_files)
        
        result["platforms"].append(platform_info)
    
    # 生成推荐
    articles = [p for p in result["platforms"] if p["article_exists"]]
    
    if len(articles) == 0:
        result["recommendation"] = {
            "action": "no_article",
            "target": None,
            "message": f"Output/ 目录存在，但未找到任何平台的 article.md"
        }
    
    elif len(articles) == 1:
        # 唯一文章，自动选择
        article = articles[0]
        result["recommendation"] = {
            "action": "auto_select",
            "target": article["article_path"],
            "platform": article["name"],
            "message": f"自动选择唯一的文章：{article['article_path']}"
        }
    
    else:
        # 多个文章，询问用户
        platform_names = [a["name"] for a in articles]
        result["recommendation"] = {
            "action": "ask_user",
            "target": None,
            "options": [a["article_path"] for a in articles],
            "message": f"发现 {len(articles)} 个平台的文章：{', '.join(platform_names)}，请选择要转换的平台"
        }
    
    return result


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="工作区结构检测器")
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="工作区目录（默认当前目录）"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出 JSON 格式（供 AI 读取）"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="美化 JSON 输出"
    )
    
    args = parser.parse_args()
    
    # 检测工作区
    result = detect_workspace(Path(args.directory))
    
    if args.json:
        # JSON 格式输出
        indent = 2 if args.pretty else None
        print(json.dumps(result, indent=indent, ensure_ascii=False))
    
    else:
        # 人类可读格式
        print("🔍 工作区检测结果")
        print("=" * 50)
        print(f"📂 工作区根目录: {result['workspace_root']}")
        print(f"📋 工作区类型: {result['workspace_type']}")
        print(f"📁 Output/ 存在: {result['output_exists']}")
        print()
        
        if result['platforms']:
            print(f"🎯 发现 {len(result['platforms'])} 个平台:")
            for p in result['platforms']:
                status = "✅" if p['article_exists'] else "❌"
                print(f"  {status} {p['name']}: {p['article_path'] or '无 article.md'}")
                if p['images_exists']:
                    print(f"     └─ 图片: {p['image_count']} 张")
            print()
        
        print("💡 推荐操作:")
        print(f"  动作: {result['recommendation']['action']}")
        print(f"  消息: {result['recommendation']['message']}")
        
        if result['recommendation'].get('target'):
            print(f"  目标: {result['recommendation']['target']}")


if __name__ == "__main__":
    main()
