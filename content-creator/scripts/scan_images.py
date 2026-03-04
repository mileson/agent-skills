#!/usr/bin/env python3
"""
图片扫描工具
扫描工作区 Materials/Medias/images/ 目录下的所有图片文件
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
    images_dir = workspace_path / "Materials" / "Medias" / "images"
    
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
    
    # 递归扫描所有图片文件（包括子目录）
    image_files = []
    for file_path in sorted(images_dir.rglob('*')):  # 使用 rglob 递归扫描
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
            # 提取文件名中的语义信息
            filename = file_path.name
            name_without_ext = file_path.stem
            
            # 计算相对于 images/ 的路径
            relative_path = file_path.relative_to(images_dir)
            
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
            # 使用相对路径，保留子目录结构
            markdown_path = f"Medias/images/{relative_path.as_posix()}"
            
            # 提取子目录信息（如果在子目录中）
            subdirectory = str(relative_path.parent) if relative_path.parent != Path('.') else None
            
            image_info = {
                "filename": filename,
                "path": str(file_path),
                "markdown_path": markdown_path,
                "subdirectory": subdirectory,  # 新增：子目录信息
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
        subdir_info = f" [目录: {img['subdirectory']}]" if img.get('subdirectory') else ""
        lines.append(f"{i}. `{img['markdown_path']}`{sequence_info}{keyword_info}{subdir_info}")
    
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
            
            # 按子目录分组显示
            subdirs = {}
            for img in result['images']:
                subdir = img.get('subdirectory') or '根目录'
                if subdir not in subdirs:
                    subdirs[subdir] = []
                subdirs[subdir].append(img)
            
            print("\n### 按目录分组\n")
            for subdir, imgs in sorted(subdirs.items()):
                print(f"**{subdir}** ({len(imgs)} 张)")
                for img in imgs:
                    print(f"  - {img['filename']}")
                print()
            
            print("### Markdown 引用格式\n")
            print("#### 在 draft.md 中使用（阶段4）：\n")
            print("```markdown")
            # 只显示前2个示例
            for i, img in enumerate(result['images'][:2]):
                print(f"![图片描述]({img['markdown_path']})")
                print()
                print("*▲ 图注说明*")
                print()
            if len(result['images']) > 2:
                print("... (共 {} 张图片，格式相同)".format(len(result['images'])))
            print("```")
            
            print("\n#### 在 article.md 中使用（阶段6，脚本清洗后）：\n")
            print("```markdown")
            # 只显示前2个示例
            for i, img in enumerate(result['images'][:2]):
                # 去掉 Medias/ 前缀，只保留 images/xxx
                platform_path = img['markdown_path'].replace('Medias/', '')
                print(f"![图片描述]({platform_path})")
                print()
                print("*▲ 图注说明*")
                print()
            if len(result['images']) > 2:
                print("... (共 {} 张图片，格式相同)".format(len(result['images'])))
            print("```")
            
            print("\n**⭐ 路径转换规则**：")
            print("- 阶段4（draft.md）：使用 `Medias/images/xxx.png`")
            print("- 阶段6（article.md）：通过 `sanitize_output_markdown.py` 确定性转换为 `images/xxx.png`")
        else:
            print("⚠️ 未找到任何图片文件")
    else:
        print(f"不支持的输出格式: {output_format}")
        sys.exit(1)


if __name__ == "__main__":
    main()
