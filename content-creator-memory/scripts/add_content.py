#!/usr/bin/env python3
"""
增量添加内容 - Add Content

功能：添加单篇新内容到索引（无需全量重建）

用法：
    python3 add_content.py \\
        --file <新内容文件路径> \\
        --output-dir <索引目录> \\
        --auto-extract

示例：
    python3 add_content.py \\
        --file ~/.claude/skills/content-creator/memories/contents/wechat/新文章.md \\
        --output-dir ~/.claude/skills/content-creator-memory/data \\
        --auto-extract
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any

# 重用 rebuild_index.py 的函数
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from rebuild_index import (
        extract_own_work_metadata,
        build_inverted_index,
        calculate_tfidf
    )
except ImportError:
    print("❌ 无法导入 rebuild_index.py 的函数", file=sys.stderr)
    sys.exit(1)


def add_content(file_path: str, output_dir: str, auto_extract: bool):
    """增量添加内容的主函数"""
    start_time = time.time()
    
    # 1. 检查文件是否存在
    file_path_obj = Path(file_path).expanduser()
    if not file_path_obj.exists():
        print(f"❌ 文件不存在: {file_path}", file=sys.stderr)
        sys.exit(1)
    
    print(f"✓ 读取文件: {file_path_obj.name}")
    
    # 2. 提取元数据
    if auto_extract:
        file_id = file_path_obj.stem.lower().replace(' ', '-').replace('，', '-')
        metadata = extract_own_work_metadata(str(file_path_obj), file_id)
        
        if not metadata:
            print("❌ 提取元数据失败", file=sys.stderr)
            sys.exit(1)
        
        print(f"✓ 提取元数据: {metadata['title'][:30]}...")
    else:
        print("❌ 当前版本仅支持 --auto-extract 模式", file=sys.stderr)
        sys.exit(1)
    
    # 3. 加载现有索引
    output_path = Path(output_dir).expanduser()
    own_works_file = output_path / "own_works.json"
    
    if own_works_file.exists():
        with open(own_works_file, 'r', encoding='utf-8') as f:
            own_works = json.load(f)
    else:
        own_works = []
    
    # 4. 检查是否已存在（更新或新增）
    existing_index = None
    for i, doc in enumerate(own_works):
        if doc['id'] == metadata['id']:
            existing_index = i
            break
    
    if existing_index is not None:
        own_works[existing_index] = metadata
        print(f"✓ 更新现有条目: #{existing_index + 1}")
    else:
        own_works.append(metadata)
        print(f"✓ 添加新条目: #{len(own_works)}")
    
    # 5. 保存更新后的索引
    with open(own_works_file, 'w', encoding='utf-8') as f:
        json.dump(own_works, f, ensure_ascii=False, indent=2)
    print(f"✓ 保存自有内容索引: {own_works_file}")
    
    # 6. 更新搜索索引
    print("✓ 更新搜索索引...")
    
    # 加载标杆案例（如果存在）
    reference_file = output_path / "reference_examples.json"
    if reference_file.exists():
        with open(reference_file, 'r', encoding='utf-8') as f:
            reference_examples = json.load(f)
    else:
        reference_examples = []
    
    # 重新构建搜索索引
    all_documents = own_works + reference_examples
    inverted_index = build_inverted_index(all_documents)
    tfidf_scores = calculate_tfidf(inverted_index, all_documents)
    
    search_index = {
        "inverted_index": inverted_index,
        "tfidf_scores": tfidf_scores
    }
    
    search_index_file = output_path / "search_index.json"
    with open(search_index_file, 'w', encoding='utf-8') as f:
        json.dump(search_index, f, ensure_ascii=False, indent=2)
    print(f"✓ 保存搜索索引: {search_index_file}")
    
    # 7. 更新元数据
    metadata_file = output_path / "metadata.json"
    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            index_metadata = json.load(f)
    else:
        index_metadata = {}
    
    index_metadata.update({
        "version": "1.0",
        "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_own_works": len(own_works),
        "total_reference_examples": len(reference_examples),
        "total_keywords": len(inverted_index)
    })
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(index_metadata, f, ensure_ascii=False, indent=2)
    print(f"✓ 更新元数据: {metadata_file}")
    
    elapsed_time = time.time() - start_time
    print(f"\n✅ 增量添加完成！耗时: {elapsed_time:.2f}s")


def main():
    parser = argparse.ArgumentParser(description='增量添加内容到索引')
    parser.add_argument('--file', required=True, help='新内容文件路径')
    parser.add_argument('--output-dir', default='~/.cursor/skills/content-creator-memory/data',
                        help='索引输出目录路径')
    parser.add_argument('--auto-extract', action='store_true', help='自动提取元数据')
    
    args = parser.parse_args()
    
    add_content(args.file, args.output_dir, args.auto_extract)


if __name__ == "__main__":
    main()
