#!/usr/bin/env python3
"""
智能内容搜索 - Smart Content Search

功能：跨平台智能搜索，支持主平台权重（80%）+ 其他平台探索（20%）

用法：
    python3 search_smart.py \\
        --query "查询词" \\
        --primary-platform <主平台> \\
        --top-k 10

示例：
    # 主要搜索即刻，探索微信
    python3 search_smart.py --query "Cursor开发" --primary-platform jike --top-k 5
    
    # 主要搜索微信，探索即刻和小红书
    python3 search_smart.py --query "AI编程" --primary-platform wechat --top-k 5
    
    # 只搜索单个平台
    python3 search_smart.py --query "产品设计" --primary-platform jike --single-platform
"""

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Any, Optional


def load_platform_data(output_dir: str, platform: str) -> tuple:
    """加载指定平台的索引数据"""
    try:
        output_path = Path(output_dir).expanduser()
        
        # 加载平台内容索引
        works_file = output_path / f"own_works_{platform}.json"
        if not works_file.exists():
            return [], {}
        
        with open(works_file, 'r', encoding='utf-8') as f:
            works = json.load(f)
        
        # 加载平台搜索索引
        search_file = output_path / f"search_index_{platform}.json"
        with open(search_file, 'r', encoding='utf-8') as f:
            search_index = json.load(f)
        
        return works, search_index
    except Exception as e:
        print(f"❌ 加载 {platform} 索引失败: {e}", file=sys.stderr)
        return [], {}


def get_available_platforms(output_dir: str) -> List[str]:
    """获取所有可用的平台"""
    output_path = Path(output_dir).expanduser()
    platforms = []
    
    for file in output_path.glob("own_works_*.json"):
        platform = file.stem.replace("own_works_", "")
        platforms.append(platform)
    
    return platforms


def calculate_relevance(query: str, document: Dict[str, Any], tfidf_scores: Dict[str, float]) -> float:
    """计算文档与查询的相关性分数"""
    query_keywords = set(query.lower().split())
    doc_keywords = set(document.get('keywords', []))
    doc_id = document['id']
    
    # 1. 关键词匹配分数（0-0.5）
    keyword_match = len(query_keywords & doc_keywords) / max(len(query_keywords), 1)
    keyword_score = keyword_match * 0.5
    
    # 2. TF-IDF 分数（0-0.5）
    tfidf_score = 0.0
    if doc_id in tfidf_scores:
        doc_tfidf = tfidf_scores[doc_id]
        for keyword in query_keywords:
            tfidf_score += doc_tfidf.get(keyword, 0)
    tfidf_score = min(tfidf_score, 0.5)
    
    # 3. 标题匹配分数（bonus）
    title = document.get('title', '').lower()
    title_match = sum(1 for keyword in query_keywords if keyword in title)
    title_bonus = min(title_match * 0.1, 0.3)
    
    total_score = keyword_score + tfidf_score + title_bonus
    return round(total_score, 4)


def search_platform(query: str, platform: str, output_dir: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """搜索单个平台"""
    works, search_index = load_platform_data(output_dir, platform)
    
    if not works:
        return []
    
    tfidf_scores = search_index.get('tfidf_scores', {})
    
    # 计算相关性分数
    results = []
    for doc in works:
        relevance = calculate_relevance(query, doc, tfidf_scores)
        if relevance > 0:
            result = {
                "id": doc['id'],
                "title": doc['title'],
                "platform": platform,
                "file_path": doc['file_path'],
                "relevance_score": relevance,
                "quality_score": doc.get('quality_score', 0),
                "word_count": doc.get('word_count', 0),
                "summary": doc.get('summary', '')[:100] + '...' if len(doc.get('summary', '')) > 100 else doc.get('summary', '')
            }
            results.append(result)
    
    # 按相关性 + 质量分数排序
    results.sort(key=lambda x: (x['relevance_score'], x['quality_score']), reverse=True)
    
    return results[:top_k]


def merge_results(primary_results: List[Dict[str, Any]], 
                  other_results: Dict[str, List[Dict[str, Any]]], 
                  primary_weight: float = 0.8,
                  top_k: int = 10) -> List[Dict[str, Any]]:
    """
    合并多平台搜索结果
    
    Args:
        primary_results: 主平台搜索结果
        other_results: 其他平台搜索结果 {platform: results}
        primary_weight: 主平台权重（默认 0.8）
        top_k: 返回结果数量
    """
    # 计算其他平台的权重（均等分配）
    other_platforms_count = len(other_results)
    if other_platforms_count > 0:
        other_weight = (1.0 - primary_weight) / other_platforms_count
    else:
        other_weight = 0.0
    
    # 为主平台结果添加加权分数
    for result in primary_results:
        result['weighted_score'] = result['relevance_score'] * primary_weight
        result['weight'] = primary_weight
    
    # 为其他平台结果添加加权分数
    all_results = primary_results.copy()
    for platform, results in other_results.items():
        for result in results:
            result['weighted_score'] = result['relevance_score'] * other_weight
            result['weight'] = other_weight
        all_results.extend(results)
    
    # 按加权分数排序
    all_results.sort(key=lambda x: (x['weighted_score'], x['quality_score']), reverse=True)
    
    return all_results[:top_k]


def smart_search(query: str, 
                primary_platform: str, 
                output_dir: str, 
                top_k: int = 10,
                single_platform: bool = False) -> Dict[str, Any]:
    """
    智能搜索：主平台 80% + 其他平台探索 20%
    
    Args:
        query: 搜索查询词
        primary_platform: 主搜索平台
        output_dir: 索引目录
        top_k: 返回结果数量
        single_platform: 是否只搜索单个平台
    """
    start_time = time.time()
    
    # 获取所有可用平台
    available_platforms = get_available_platforms(output_dir)
    
    if primary_platform not in available_platforms:
        return {
            "error": f"平台 {primary_platform} 不存在",
            "available_platforms": available_platforms
        }
    
    # 搜索主平台
    primary_results = search_platform(query, primary_platform, output_dir, top_k=top_k)
    
    if single_platform:
        # 只返回主平台结果
        return {
            "query": query,
            "primary_platform": primary_platform,
            "single_platform_mode": True,
            "results": primary_results,
            "total_found": len(primary_results),
            "search_time_ms": int((time.time() - start_time) * 1000)
        }
    
    # 搜索其他平台（探索）
    other_results = {}
    for platform in available_platforms:
        if platform != primary_platform:
            results = search_platform(query, platform, output_dir, top_k=5)  # 其他平台取前5
            if results:
                other_results[platform] = results
    
    # 合并结果
    merged_results = merge_results(primary_results, other_results, primary_weight=0.8, top_k=top_k)
    
    # 统计信息
    platform_stats = {
        primary_platform: {
            "weight": 0.8,
            "results_count": len([r for r in merged_results if r['platform'] == primary_platform])
        }
    }
    
    other_platforms_count = len(other_results)
    if other_platforms_count > 0:
        other_weight = 0.2 / other_platforms_count
        for platform in other_results.keys():
            platform_stats[platform] = {
                "weight": round(other_weight, 2),
                "results_count": len([r for r in merged_results if r['platform'] == platform])
            }
    
    return {
        "query": query,
        "primary_platform": primary_platform,
        "primary_weight": 0.8,
        "platform_stats": platform_stats,
        "results": merged_results,
        "total_found": len(merged_results),
        "search_time_ms": int((time.time() - start_time) * 1000)
    }


def main():
    parser = argparse.ArgumentParser(description='智能内容搜索（支持平台权重）')
    parser.add_argument('--query', required=True, help='搜索查询词')
    parser.add_argument('--primary-platform', required=True, help='主搜索平台（80%权重）')
    parser.add_argument('--top-k', type=int, default=10, help='返回结果数量')
    parser.add_argument('--output-dir', default='../data', help='索引目录路径')
    parser.add_argument('--single-platform', action='store_true', help='只搜索单个平台')
    
    args = parser.parse_args()
    
    result = smart_search(
        query=args.query,
        primary_platform=args.primary_platform,
        output_dir=args.output_dir,
        top_k=args.top_k,
        single_platform=args.single_platform
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
