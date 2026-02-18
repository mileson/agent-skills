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


def extract_xhs_tags(content: str) -> List[str]:
    """从小红书内容中提取 #xxx[话题]# 格式的话题标签"""
    tags = re.findall(r'#([^#\[]+)\[话题\]#', content)
    return [tag.strip() for tag in tags if tag.strip()]


def extract_xhs_title(file_path: str, content: str) -> str:
    """小红书笔记标题提取：优先使用文件夹名（即笔记标题）"""
    # 小红书笔记的文件夹名就是标题
    folder_name = Path(file_path).parent.name
    if folder_name and folder_name != '.' and folder_name != '2025' and folder_name != '2026':
        return folder_name
    # 回退到通用标题提取
    return extract_title(content)


def extract_xhs_body(content: str) -> str:
    """提取小红书笔记正文（去除末尾的话题标签行）"""
    lines = content.strip().split('\n')
    # 从末尾向前找到最后一行含话题标签的行，去掉它
    body_lines = []
    for line in lines:
        # 如果整行都是 #话题# 标签，跳过
        stripped = line.strip()
        if stripped and re.match(r'^(#[^#]+\[话题\]#[\s]*)+$', stripped):
            continue
        body_lines.append(line)
    return '\n'.join(body_lines).strip()


def count_images_in_folder(file_path: str) -> int:
    """统计文件所在文件夹中的图片数量"""
    folder = Path(file_path).parent
    image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.heic'}
    return len([f for f in folder.iterdir() if f.suffix.lower() in image_exts])


def extract_summary(content: str, max_length: int = 200) -> str:
    """提取文章摘要（前200字）"""
    # 移除 Markdown 标记
    content = re.sub(r'#+ ', '', content)  # 移除标题标记
    content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)  # 移除链接
    content = re.sub(r'[*_`]', '', content)  # 移除格式标记
    # 移除小红书话题标签
    content = re.sub(r'#[^#]+\[话题\]#', '', content)
    
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


def extract_keywords(title: str, content: str, top_k: int = 10, xhs_tags: List[str] = None) -> List[str]:
    """提取关键词（支持小红书话题标签优先）"""
    text = (title + ' ' + content).lower()
    
    # 移除 Markdown 语法和小红书话题标签格式
    text = re.sub(r'#[^#]*\[话题\]#', ' ', text)
    text = re.sub(r'[#*_`\[\]()]', ' ', text)
    
    # 提取中文词（2-4字）和英文词
    chinese_words = re.findall(r'[\u4e00-\u9fff]{2,4}', text)
    english_words = re.findall(r'\b[a-z]{3,}\b', text)
    
    # 停用词
    stop_words = {'的', '了', '是', '在', '和', '我', '你', '他', '她', '它',
                  '这', '那', '都', '也', '就', '还', '会', '能', '有', '不',
                  '吗', '呢', '吧', '啊', '呀', '哦', '嘛', '嗯',
                  'the', 'and', 'for', 'with', 'this', 'that', 'from'}
    
    # 统计词频
    word_freq = defaultdict(int)
    for word in chinese_words + english_words:
        if word not in stop_words:
            word_freq[word] += 1
    
    # 如果有小红书话题标签，优先加入（高权重）
    priority_keywords = []
    if xhs_tags:
        for tag in xhs_tags:
            tag_lower = tag.lower()
            if tag_lower not in priority_keywords:
                priority_keywords.append(tag_lower)
    
    # 返回 Top-K（话题标签优先 + 高频词补充）
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    remaining_keywords = [word for word, freq in sorted_words 
                         if word not in priority_keywords]
    
    combined = priority_keywords + remaining_keywords
    return combined[:max(top_k, len(priority_keywords))]


def detect_platform_from_path(file_path: str) -> str:
    """从文件路径推断平台"""
    if '/xhs/' in file_path:
        return 'xhs'
    elif '/wechat/' in file_path:
        return 'wechat'
    elif '/jike/' in file_path:
        return 'jike'
    return 'unknown'


def extract_own_work_metadata(file_path: str, file_id: str) -> Dict[str, Any]:
    """提取自有内容的元数据（支持多平台格式）"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        platform = detect_platform_from_path(file_path)
        
        # 小红书笔记特殊处理
        if platform == 'xhs':
            title = extract_xhs_title(file_path, content)
            xhs_tags = extract_xhs_tags(content)
            body = extract_xhs_body(content)
            summary = extract_summary(body, max_length=200)
            word_count = calculate_word_count(body)
            keywords = extract_keywords(title, body, top_k=15, xhs_tags=xhs_tags)
            image_count = count_images_in_folder(file_path)
            
            # 小红书质量评分（短内容友好）
            # 基础分6分 + 字数加成(max 1.5) + 图片加成(max 1.0) + 标签加成(max 0.5) + 结构加成(max 1.0)
            qs = 6.0
            qs += min(1.5, word_count / 200)  # 每200字加1分，最多1.5
            qs += min(1.0, image_count * 0.25)  # 每张图加0.25，最多1.0
            qs += min(0.5, len(xhs_tags) * 0.1)  # 每个标签加0.1，最多0.5
            # 结构加成：含emoji/列表/分段
            if re.search(r'[\U0001F300-\U0001F9FF]', content):
                qs += 0.3
            if re.search(r'^\d️⃣|^[①②③④⑤]|^[\-\*] ', content, re.MULTILINE):
                qs += 0.4
            if content.count('\n\n') >= 2:
                qs += 0.3
            quality_score = min(10.0, qs)
            
            metadata = {
                "id": file_id,
                "file_path": os.path.relpath(file_path, Path.home()),
                "title": title,
                "summary": summary,
                "word_count": word_count,
                "quality_score": round(quality_score, 1),
                "keywords": keywords,
                "xhs_tags": xhs_tags,
                "image_count": image_count,
                "content_type": "XHS_Note",
                "target_audience": [],
                "technical_stack": [],
                "reusable_elements": {
                    "title_hook": title,  # 小红书标题即钩子
                    "golden_sentences": [],
                    "core_workflows": []
                }
            }
        else:
            # 通用处理（wechat/jike/其他）
            title = extract_title(content)
            summary = extract_summary(content)
            word_count = calculate_word_count(content)
            keywords = extract_keywords(title, content)
            
            # 通用质量评分（基于字数和结构）
            quality_score = min(10.0, 5.0 + (word_count / 500))
            
            metadata = {
                "id": file_id,
                "file_path": os.path.relpath(file_path, Path.home()),
                "title": title,
                "summary": summary,
                "word_count": word_count,
                "quality_score": round(quality_score, 1),
                "keywords": keywords,
                "content_type": "Article",
                "target_audience": [],
                "technical_stack": [],
                "reusable_elements": {
                    "golden_sentences": [],
                    "core_workflows": []
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
    
    # 3. 构建索引（分别为自有内容和标杆案例生成独立索引）
    print("\n🔨 构建索引...")
    output_path = Path(output_dir).expanduser()
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 3a. 自有内容索引（按平台分离）
    if own_works:
        # 按平台分组
        platform_groups = defaultdict(list)
        for work in own_works:
            # 从文件路径推断平台（如 contents/wechat/... -> wechat）
            fp = work.get('file_path', '')
            platform = 'unknown'
            if '/wechat/' in fp:
                platform = 'wechat'
            elif '/jike/' in fp:
                platform = 'jike'
            elif '/xhs/' in fp:
                platform = 'xhs'
            work['platform'] = platform
            platform_groups[platform].append(work)
        
        for platform, works in platform_groups.items():
            # 保存自有内容
            own_works_file = output_path / f"own_works_{platform}.json"
            with open(own_works_file, 'w', encoding='utf-8') as f:
                json.dump(works, f, ensure_ascii=False, indent=2)
            print(f"✓ 自有内容索引 ({platform}): {own_works_file} ({len(works)} 篇)")
            
            # 构建并保存该平台的搜索索引
            inv_idx = build_inverted_index(works)
            tfidf = calculate_tfidf(inv_idx, works)
            search_idx = {"inverted_index": inv_idx, "tfidf_scores": tfidf}
            search_index_file = output_path / f"search_index_{platform}.json"
            with open(search_index_file, 'w', encoding='utf-8') as f:
                json.dump(search_idx, f, ensure_ascii=False, indent=2)
            print(f"✓ 搜索索引 ({platform}): {search_index_file} ({len(inv_idx)} 关键词)")
    
    # 3b. 标杆案例索引（独立生成 search_index_reference.json）
    reference_file = output_path / "reference_examples.json"
    with open(reference_file, 'w', encoding='utf-8') as f:
        json.dump(reference_examples, f, ensure_ascii=False, indent=2)
    print(f"✓ 标杆案例索引: {reference_file} ({len(reference_examples)} 篇)")
    
    if reference_examples:
        ref_inv_idx = build_inverted_index(reference_examples)
        ref_tfidf = calculate_tfidf(ref_inv_idx, reference_examples)
        ref_search_index = {"inverted_index": ref_inv_idx, "tfidf_scores": ref_tfidf}
        ref_search_index_file = output_path / "search_index_reference.json"
        with open(ref_search_index_file, 'w', encoding='utf-8') as f:
            json.dump(ref_search_index, f, ensure_ascii=False, indent=2)
        print(f"✓ 标杆案例搜索索引: {ref_search_index_file} ({len(ref_inv_idx)} 关键词)")
    
    # 4. 统计所有关键词总数
    all_documents = own_works + reference_examples
    all_inverted_index = build_inverted_index(all_documents)
    
    # 5. 保存元数据
    print("\n💾 保存元数据...")
    platform_stats = {}
    if own_works:
        for platform, works in platform_groups.items():
            platform_stats[platform] = len(works)
    
    metadata = {
        "version": "2.0",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_own_works": len(own_works),
        "own_works_by_platform": platform_stats,
        "total_reference_examples": len(reference_examples),
        "total_keywords": len(all_inverted_index)
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
