#!/usr/bin/env python3
"""
拆分即刻动态文件 - Split Jike Posts

功能: 将单个包含多条动态的 Markdown 文件拆分为独立的文件

用法:
    python3 split_jike_posts.py \\
        --input <输入文件路径> \\
        --output-dir <输出目录>

示例:
    python3 split_jike_posts.py \\
        --input ~/.cursor/skills/content-creator-memory/memories/contents/jike/超级峰_即刻动态_20241108_20260126_1025条.md \\
        --output-dir ~/.cursor/skills/content-creator-memory/memories/contents/jike/posts
"""

import argparse
import re
from pathlib import Path
from datetime import datetime


def parse_date(date_str: str) -> str:
    """解析日期并转换为 YYYY-MM-DD 格式"""
    try:
        # 解析 "11/8/2024, 9:46:00 AM" 格式
        dt = datetime.strptime(date_str.strip(), "%m/%d/%Y, %I:%M:%S %p")
        return dt.strftime("%Y-%m-%d")
    except Exception as e:
        print(f"⚠️  日期解析失败: {date_str}, 使用默认日期")
        return "unknown-date"


def split_jike_posts(input_file: str, output_dir: str):
    """拆分即刻动态文件"""
    
    input_path = Path(input_file).expanduser()
    output_path = Path(output_dir).expanduser()
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"📖 读取文件: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 按 "---" 分割动态
    posts = content.split('\n---\n')
    print(f"✓ 发现 {len(posts)} 条动态")
    
    success_count = 0
    
    for i, post in enumerate(posts, 1):
        post = post.strip()
        if not post:
            continue
        
        # 提取动态元数据
        lines = post.split('\n')
        
        # 提取动态编号（从 "## 动态 X" 中）
        post_num_match = re.search(r'## 动态 (\d+)', lines[0])
        post_num = post_num_match.group(1) if post_num_match else str(i)
        
        # 提取发布时间
        pub_time = "unknown-date"
        circle = "未知圈子"
        content_text = ""
        
        for line in lines:
            if line.startswith('**发布时间：**'):
                pub_time = parse_date(line.replace('**发布时间：**', '').strip())
            elif line.startswith('**圈子：**'):
                circle = line.replace('**圈子：**', '').strip()
            elif line.startswith('**内容：**'):
                # 内容从下一行开始
                idx = lines.index(line)
                # 提取内容（直到遇到 "**图片：**" 或文件结束）
                content_lines = []
                for j in range(idx + 1, len(lines)):
                    if lines[j].startswith('**图片：**') or lines[j].startswith('---'):
                        break
                    content_lines.append(lines[j])
                content_text = '\n'.join(content_lines).strip()
                break
        
        # 生成文件名: YYYY-MM-DD_动态编号_圈子.md
        # 清理圈子名称中的特殊字符
        safe_circle = re.sub(r'[^\w\s-]', '', circle).replace(' ', '-')[:30]
        filename = f"{pub_time}_post{post_num.zfill(4)}_{safe_circle}.md"
        
        # 构建新的 Markdown 内容
        new_content = f"""# 即刻动态 {post_num}

**发布时间:** {pub_time}  
**圈子:** {circle}

---

{content_text}
"""
        
        # 保存文件
        output_file = output_path / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        success_count += 1
        
        if success_count % 100 == 0:
            print(f"✓ 已处理 {success_count} 条动态...")
    
    print(f"\n✅ 拆分完成！共生成 {success_count} 个文件")
    print(f"📂 输出目录: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='拆分即刻动态文件')
    parser.add_argument('--input', required=True, help='输入文件路径')
    parser.add_argument('--output-dir', required=True, help='输出目录路径')
    
    args = parser.parse_args()
    
    split_jike_posts(args.input, args.output_dir)


if __name__ == "__main__":
    main()
