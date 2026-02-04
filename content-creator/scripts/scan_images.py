#!/usr/bin/env python3
"""
图片扫描工具
扫描工作区 Medias/images/ 目录下的所有图片文件
输出 markdown-to-wechat 兼容的格式
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict

# 支持的图片格式
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp'}

def scan_images(workspace_path: str = None) -> Dict:
    """
    扫描工作区的图片文件
    
    Args:
        workspace_path: 工作区路径，默认为当前目录
    
    Returns:
        Dict: 包含图片信息的字典
    """
    if workspace_path is None:
        workspace_path = os.getcwd()
    
    workspace_path = Path(workspace_path)
    images_dir = workspace_path / "Medias" / "images"
    
    result = {
        "workspace": str(workspace_path),
        "images_dir": str(images_dir),
        "exists": images_dir.exists(),
        "total_images": 0,
        "images": []
    }
    
    if not images_dir.exists():
        result["error"] = f"图片目录不存在: {images_dir}"
        return result
    
    # 扫描所有图片文件
    image_files = []
    for file_path in sorted(images_dir.iterdir()):
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
            # 提取文件名中的语义信息
            filename = file_path.name
            name_without_ext = file_path.stem
            
            # 尝试提取序号（如 01-preview.png -> 序号: 01）
            sequence = None
            keyword = name_without_ext
            if '-' in name_without_ext:
                parts = name_without_ext.split('-', 1)
                if parts[0].isdigit():
                    sequence = int(parts[0])
                    keyword = parts[1] if len(parts) > 1 else name_without_ext
            elif '_' in name_without_ext:
                parts = name_without_ext.split('_', 1)
                if parts[0].isdigit():
                    sequence = int(parts[0])
                    keyword = parts[1] if len(parts) > 1 else name_without_ext
            
            # 构造 markdown-to-wechat 兼容的路径格式
            markdown_path = f"Medias/images/{filename}"
            
            image_info = {
                "filename": filename,
                "path": str(file_path),
                "markdown_path": markdown_path,
                "sequence": sequence,
                "keyword": keyword,
                "size": file_path.stat().st_size,
                "extension": file_path.suffix.lower()
            }
            
            image_files.append(image_info)
    
    result["total_images"] = len(image_files)
    result["images"] = image_files
    
    return result


def format_markdown_list(images: List[Dict]) -> str:
    """
    格式化为 Markdown 列表
    
    Args:
        images: 图片信息列表
    
    Returns:
        str: Markdown 格式的图片列表
    """
    if not images:
        return "无可用图片"
    
    lines = []
    for i, img in enumerate(images, 1):
        sequence_info = f" (序号: {img['sequence']})" if img['sequence'] is not None else ""
        keyword_info = f" [关键词: {img['keyword']}]" if img['keyword'] else ""
        lines.append(f"{i}. `{img['markdown_path']}`{sequence_info}{keyword_info}")
    
    return "\n".join(lines)


def main():
    """
    命令行入口
    """
    # 解析命令行参数
    workspace_path = sys.argv[1] if len(sys.argv) > 1 else None
    output_format = sys.argv[2] if len(sys.argv) > 2 else "json"
    
    # 扫描图片
    result = scan_images(workspace_path)
    
    # 输出结果
    if output_format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif output_format == "markdown":
        print(f"## 图片扫描结果\n")
        print(f"- 工作区: `{result['workspace']}`")
        print(f"- 图片目录: `{result['images_dir']}`")
        print(f"- 目录存在: {'✅ 是' if result['exists'] else '❌ 否'}")
        print(f"- 图片总数: **{result['total_images']}** 张\n")
        
        if result.get('error'):
            print(f"❌ 错误: {result['error']}")
        elif result['total_images'] > 0:
            print("### 图片清单\n")
            print(format_markdown_list(result['images']))
            print("\n### Markdown 引用格式\n")
            print("```markdown")
            for img in result['images']:
                print(f"![图片描述]({img['markdown_path']})")
                print()
                print("*▲ 图注说明*")
                print()
            print("```")
        else:
            print("⚠️ 未找到任何图片文件")
    else:
        print(f"不支持的输出格式: {output_format}")
        sys.exit(1)


if __name__ == "__main__":
    main()
