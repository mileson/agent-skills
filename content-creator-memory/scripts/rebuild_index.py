#!/usr/bin/env python3
"""
全量重建索引 - Rebuild Index

功能：扫描自有内容和标杆案例目录，提取元数据，构建完整索引

用法：
    python3 rebuild_index.py \\
        --contents-dir <自有内容目录> \\
        --examples-dir <标杆案例目录> \\
        --output-dir <索引输出目录>

示例：
    python3 rebuild_index.py \\
        --contents-dir ~/.claude/skills/content-creator/memories/contents/wechat \\
        --examples-dir ~/.claude/skills/content-creator/memories/examples/wechat \\
        --output-dir ~/.claude/skills/content-creator-memory/data
"""

import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Any


def extract_title(content: str) -> str:
    """从 Markdown 内容中提取标题"""
    lines = content.strip().split('\n')
    for line in lines[:10]:  # 只检查前10行
        line = line.strip()
        if line.startswith('# '):
            return line[2:].strip()
    # 如果没有找到一级标题，返回第一行非空内容
    for line in lines[:5]:
        line = line.strip()
        if line:
            return line[:100]  # 限制长度
    return "无标题"


def extract_summary(content: str, max_length: int = 200) -> str:
    """提取文章摘要（前200字）"""
    # 移除 Markdown 标记
    content = re.sub(r'#+ ', '', content)  # 移除标题标记
    content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)  # 移除链接
    content = re.sub(r'[*_`]', '', content)  # 移除格式标记
    
    # 提取前几段文字
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    summary = ' '.join(paragraphs[:3])  # 前3段
    
    if len(summary) > max_length:
        summary = summary[:max_length] + '...'
    
    return summary


def calculate_word_count(content: str) -> int:
    """计算字数（中文字符 + 英文单词）"""
    # 中文字符
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
    # 英文单词
    english_words = len(re.findall(r'\b[a-zA-Z]+\b', content))
    return chinese_chars + english_words


def extract_keywords(title: str, content: str, top_k: int = 10) -> List[str]:
    """提取关键词（简单版本：基于标题和内容的高频词）"""
    text = (title + ' ' + content).lower()
    
    # 移除 Markdown 语法
    text = re.sub(r'[#*_`\[\]()]', ' ', text)
    
    # 提取中文词（2-4字）和英文词
    chinese_words = re.findall(r'[\u4e00-\u9fff]{2,4}', text)
    english_words = re.findall(r'\b[a-z]{3,}\b', text)
    
    # 统计词频
    word_freq = defaultdict(int)
    for word in chinese_words + english_words:
        if word not in ['的', '了', '是', '在', '和', 'the', 'and', 'for', 'with']:
            word_freq[word] += 1
    
    # 返回 Top-K
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:top_k]]


def extract_own_work_metadata(file_path: str, file_id: str) -> Dict[str, Any]:
    """提取自有内容的元数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        title = extract_title(content)
        summary = extract_summary(content)
        word_count = calculate_word_count(content)
        keywords = extract_keywords(title, content)
        
        # 简单的质量评分（基于字数和结构）
        quality_score = min(10.0, 5.0 + (word_count / 500))  # 基础分5分，每500字加1分
        
        metadata = {
            "id": file_id,
            "file_path": os.path.relpath(file_path, Path.home()),
            "title": title,
            "summary": summary,
            "word_count": word_count,
            "quality_score": round(quality_score, 1),
            "keywords": keywords,
            "content_type": "Article",  # 默认类型
            "target_audience": [],  # 需要手动标注或 AI 提取
            "technical_stack": [],  # 需要手动标注或 AI 提取
            "reusable_elements": {
                "golden_sentences": [],  # 需要手动标注或 AI 提取
                "core_workflows": []  # 需要手动标注或 AI 提取
            }
        }
        
        return metadata
    except Exception as e:
        print(f"❌ 提取元数据失败: {file_path}, 错误: {e}", file=sys.stderr)
        return None


def extract_reference_metadata(file_path: str, file_id: str, author: str) -> Dict[str, Any]:
    """提取标杆案例的元数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        title = extract_title(content)
        keywords = extract_keywords(title, content)
        
        # 简单的标题钩子分析
        title_hooks = []
        if re.search(r'\d+', title):
            title_hooks.append("数字钩子")
        if any(word in title for word in ['惊艳', '震撼', '爆款', '颠覆', '必看']):
            title_hooks.append("情绪词汇")
        if '？' in title or '!' in title:
            title_hooks.append("问句/感叹")
        
        metadata = {
            "id": file_id,
            "file_path": os.path.relpath(file_path, Path.home()),
            "title": title,
            "author": author,
            "platform": "wechat",  # 默认平台
            "keywords": keywords,
            "title_hooks": title_hooks,
            "structural_patterns": [],  # 需要手动标注或 AI 提取
            "expression_techniques": []  # 需要手动标注或 AI 提取
        }
        
        return metadata
    except Exception as e:
        print(f"❌ 提取元数据失败: {file_path}, 错误: {e}", file=sys.stderr)
        return None


def build_inverted_index(documents: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """构建倒排索引（关键词 -> 文档ID列表）"""
    inverted_index = defaultdict(list)
    
    for doc in documents:
        doc_id = doc['id']
        keywords = doc.get('keywords', [])
        
        for keyword in keywords:
            if doc_id not in inverted_index[keyword]:
                inverted_index[keyword].append(doc_id)
    
    return dict(inverted_index)


def calculate_tfidf(inverted_index: Dict[str, List[str]], documents: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """计算 TF-IDF 分数"""
    import math
    
    total_docs = len(documents)
    tfidf_scores = {}
    
    # 构建文档ID到文档的映射
    doc_map = {doc['id']: doc for doc in documents}
    
    for keyword, doc_ids in inverted_index.items():
        idf = math.log(total_docs / len(doc_ids))  # IDF
        
        for doc_id in doc_ids:
            doc = doc_map.get(doc_id)
            if doc:
                keywords = doc.get('keywords', [])
                tf = keywords.count(keyword) / len(keywords) if keywords else 0
                
                if doc_id not in tfidf_scores:
                    tfidf_scores[doc_id] = {}
                
                tfidf_scores[doc_id][keyword] = round(tf * idf, 4)
    
    return tfidf_scores


def rebuild_index(contents_dir: str, examples_dir: str, output_dir: str):
    """重建索引的主函数"""
    start_time = time.time()
    
    print("🔍 开始扫描文件...")
    
    # 1. 扫描自有内容（递归扫描所有子目录）
    own_works = []
    contents_path = Path(contents_dir).expanduser()
    
    if contents_path.exists():
        md_files = list(contents_path.rglob("*.md"))  # 使用 rglob 递归扫描
        print(f"✓ 发现自有内容: {len(md_files)} 篇")
        
        for file_path in md_files:
            file_id = file_path.stem.lower().replace(' ', '-').replace('，', '-')
            metadata = extract_own_work_metadata(str(file_path), file_id)
            if metadata:
                own_works.append(metadata)
        
        print(f"✓ 成功提取: {len(own_works)} 篇自有内容")
    else:
        print(f"⚠️  自有内容目录不存在: {contents_path}")
    
    # 2. 扫描标杆案例（递归扫描所有作者目录）
    reference_examples = []
    examples_path = Path(examples_dir).expanduser()
    
    if examples_path.exists():
        author_dirs = [d for d in examples_path.iterdir() if d.is_dir()]
        print(f"✓ 发现作者目录: {len(author_dirs)} 个")
        
        for author_dir in author_dirs:
            author = author_dir.name
            md_files = list(author_dir.rglob("*.md"))  # 使用 rglob 支持嵌套子目录
            
            for file_path in md_files:
                file_id = f"{author.lower().replace(' ', '-')}-{file_path.stem.lower().replace(' ', '-')}"
                metadata = extract_reference_metadata(str(file_path), file_id, author)
                if metadata:
                    reference_examples.append(metadata)
        
        print(f"✓ 成功提取: {len(reference_examples)} 篇标杆案例")
    else:
        print(f"⚠️  标杆案例目录不存在: {examples_path}")
    
    # 3. 构建倒排索引
    print("\n🔨 构建倒排索引...")
    all_documents = own_works + reference_examples
    inverted_index = build_inverted_index(all_documents)
    print(f"✓ 倒排索引: {len(inverted_index)} 个关键词")
    
    # 4. 计算 TF-IDF
    print("📊 计算 TF-IDF 分数...")
    tfidf_scores = calculate_tfidf(inverted_index, all_documents)
    print(f"✓ TF-IDF 计算完成: {len(tfidf_scores)} 个文档")
    
    # 5. 保存索引文件
    print("\n💾 保存索引文件...")
    output_path = Path(output_dir).expanduser()
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 保存自有内容索引
    own_works_file = output_path / "own_works.json"
    with open(own_works_file, 'w', encoding='utf-8') as f:
        json.dump(own_works, f, ensure_ascii=False, indent=2)
    print(f"✓ 自有内容索引: {own_works_file}")
    
    # 保存标杆案例索引
    reference_file = output_path / "reference_examples.json"
    with open(reference_file, 'w', encoding='utf-8') as f:
        json.dump(reference_examples, f, ensure_ascii=False, indent=2)
    print(f"✓ 标杆案例索引: {reference_file}")
    
    # 保存搜索索引
    search_index = {
        "inverted_index": inverted_index,
        "tfidf_scores": tfidf_scores
    }
    search_index_file = output_path / "search_index.json"
    with open(search_index_file, 'w', encoding='utf-8') as f:
        json.dump(search_index, f, ensure_ascii=False, indent=2)
    print(f"✓ 搜索索引: {search_index_file}")
    
    # 保存元数据
    metadata = {
        "version": "1.0",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_own_works": len(own_works),
        "total_reference_examples": len(reference_examples),
        "total_keywords": len(inverted_index)
    }
    metadata_file = output_path / "metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"✓ 元数据: {metadata_file}")
    
    elapsed_time = time.time() - start_time
    print(f"\n✅ 索引重建完成！耗时: {elapsed_time:.1f}s")


def main():
    parser = argparse.ArgumentParser(description='全量重建内容索引')
    parser.add_argument('--contents-dir', required=True, help='自有内容目录路径')
    parser.add_argument('--examples-dir', required=True, help='标杆案例目录路径')
    parser.add_argument('--output-dir', required=True, help='索引输出目录路径')
    
    args = parser.parse_args()
    
    rebuild_index(args.contents_dir, args.examples_dir, args.output_dir)


if __name__ == "__main__":
    main()
