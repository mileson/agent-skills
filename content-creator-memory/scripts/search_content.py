#!/usr/bin/env python3
"""
搜索自有内容 - Search Content (支持平台分离)

功能：基于查询词和过滤条件检索自有内容（支持按平台搜索）

用法：
    python3 search_content.py \\
        --query "查询词" \\
        --platform <平台名> \\
        --filters "field:value,field:value" \\
        --top-k 5 \\
        --min-quality 6.0

示例：
    # 搜索即刻动态
    python3 search_content.py --query "Cursor开发" --platform jike --top-k 5
    
    # 搜索微信文章
    python3 search_content.py --query "AI编程" --platform wechat --top-k 3
    
    # 搜索所有平台（默认）
    python3 search_content.py --query "产品设计" --platform all --top-k 10
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional


def get_available_platforms(output_dir: str) -> List[str]:
    """获取所有可用的平台"""
    output_path = Path(output_dir).expanduser()
    platforms = []
    
    for file in output_path.glob("own_works_*.json"):
        platform = file.stem.replace("own_works_", "")
        platforms.append(platform)
    
    return platforms


def load_index_data(output_dir: str, platform: str = 'all') -> tuple:
    """加载索引数据（支持平台参数）"""
    try:
        output_path = Path(output_dir).expanduser()
        
        if platform == 'all':
            # 加载所有平台的索引
            available_platforms = get_available_platforms(output_dir)
            all_works = []
            all_search_indices = {}
            
            for p in available_platforms:
                with open(output_path / f"own_works_{p}.json", 'r', encoding='utf-8') as f:
                    works = json.load(f)
                    all_works.extend(works)
                
                with open(output_path / f"search_index_{p}.json", 'r', encoding='utf-8') as f:
                    search_index = json.load(f)
                    all_search_indices[p] = search_index
            
            # 合并搜索索引
            merged_search_index = {
                "inverted_index": {},
                "tfidf_scores": {}
            }
            for p, idx in all_search_indices.items():
                merged_search_index["inverted_index"].update(idx.get("inverted_index", {}))
                merged_search_index["tfidf_scores"].update(idx.get("tfidf_scores", {}))
            
            return all_works, merged_search_index
        else:
            # 加载指定平台的索引
            works_file = output_path / f"own_works_{platform}.json"
            search_file = output_path / f"search_index_{platform}.json"
            
            if not works_file.exists():
                print(f"❌ 平台 {platform} 的索引不存在", file=sys.stderr)
                print(f"可用平台: {', '.join(get_available_platforms(output_dir))}", file=sys.stderr)
                sys.exit(1)
            
            with open(works_file, 'r', encoding='utf-8') as f:
                own_works = json.load(f)
            
            with open(search_file, 'r', encoding='utf-8') as f:
                search_index = json.load(f)
            
            return own_works, search_index
    except Exception as e:
        print(f"❌ 加载索引失败: {e}", file=sys.stderr)
        sys.exit(1)


def parse_filters(filters_str: Optional[str]) -> Dict[str, str]:
    """解析过滤条件字符串"""
    if not filters_str:
        return {}
    
    filters = {}
    for item in filters_str.split(','):
        if ':' in item:
            key, value = item.split(':', 1)
            filters[key.strip()] = value.strip()
    
    return filters


def apply_filters(documents: List[Dict[str, Any]], filters: Dict[str, str]) -> List[Dict[str, Any]]:
    """应用过滤条件"""
    if not filters:
        return documents
    
    filtered = []
    for doc in documents:
        match = True
        
        for key, value in filters.items():
            if key in doc:
                doc_value = doc[key]
                
                # 处理列表字段
                if isinstance(doc_value, list):
                    if value not in doc_value:
                        match = False
                        break
                # 处理字符串字段
                elif isinstance(doc_value, str):
                    if value.lower() not in doc_value.lower():
                        match = False
                        break
                # 处理其他类型
                else:
                    if str(value) != str(doc_value):
                        match = False
                        break
            else:
                match = False
                break
        
        if match:
            filtered.append(doc)
    
    return filtered


def calculate_relevance_score(query: str, doc: Dict[str, Any], search_index: Dict[str, Any]) -> float:
    """计算文档与查询的相关度分数"""
    score = 0.0
    query_lower = query.lower()
    
    # 1. 标题匹配（权重：40%）
    title = doc.get('title', '').lower()
    if query_lower in title:
        score += 0.4
    
    # 2. 关键词匹配（权重：30%）
    keywords = doc.get('keywords', [])
    for keyword in keywords:
        if query_lower in keyword.lower() or keyword.lower() in query_lower:
            score += 0.3 / len(keywords)  # 平均分配权重
    
    # 3. TF-IDF 匹配（权重：20%）
    doc_id = doc.get('id')
    tfidf_scores = search_index.get('tfidf_scores', {}).get(doc_id, {})
    
    # 检查查询词是否在 TF-IDF 中
    for keyword in query.split():
        if keyword.lower() in tfidf_scores:
            score += tfidf_scores[keyword.lower()] * 0.2
    
    # 4. 摘要匹配（权重：10%）
    summary = doc.get('summary', '').lower()
    if query_lower in summary:
        score += 0.1
    
    return min(1.0, score)  # 限制在 [0, 1] 范围


def search_content(query: str, filters: Dict[str, str], top_k: int, min_quality: float, output_dir: str) -> Dict[str, Any]:
    """搜索自有内容的主函数"""
    start_time = time.time()
    
    # 1. 加载索引数据
    own_works, search_index = load_index_data(output_dir)
    
    # 2. 应用过滤条件
    filtered = apply_filters(own_works, filters)
    
    # 3. 质量筛选
    filtered = [doc for doc in filtered if doc.get('quality_score', 0) >= min_quality]
    
    # 4. 计算相关度分数
    results = []
    for doc in filtered:
        relevance = calculate_relevance_score(query, doc, search_index)
        results.append({
            "document": doc,
            "relevance_score": round(relevance, 4)
        })
    
    # 5. 排序并返回 Top-K
    results.sort(key=lambda x: (x['relevance_score'], x['document'].get('quality_score', 0)), reverse=True)
    top_results = results[:top_k]
    
    # 6. 格式化输出
    output = {
        "results": [
            {
                "id": item['document']['id'],
                "title": item['document']['title'],
                "file_path": item['document']['file_path'],
                "relevance_score": item['relevance_score'],
                "quality_score": item['document'].get('quality_score', 0),
                "reusable_elements": item['document'].get('reusable_elements', {})
            }
            for item in top_results
        ],
        "total_found": len(results),
        "search_time_ms": int((time.time() - start_time) * 1000)
    }
    
    return output


def main():
    parser = argparse.ArgumentParser(description='搜索自有内容（支持平台分离）')
    parser.add_argument('--query', required=True, help='搜索查询词')
    parser.add_argument('--platform', default='all', help='搜索平台（jike/wechat/xhs/all，默认：all）')
    parser.add_argument('--filters', help='过滤条件（格式：field:value,field:value）')
    parser.add_argument('--top-k', type=int, default=5, help='返回结果数量（默认：5）')
    parser.add_argument('--min-quality', type=float, default=6.0, help='最低质量分数（默认：6.0）')
    parser.add_argument('--output-dir', default='~/.cursor/skills/content-creator-memory/data', 
                        help='索引数据目录路径')
    
    args = parser.parse_args()
    
    filters = parse_filters(args.filters)
    
    # 加载指定平台的索引
    own_works, search_index = load_index_data(args.output_dir, args.platform)
    
    # 执行搜索
    start_time = time.time()
    
    # 1. 解析过滤条件
    filters = parse_filters(args.filters)
    
    # 2. 应用过滤条件
    filtered_docs = apply_filters(own_works, filters)
    
    # 3. 质量分数过滤
    filtered_docs = [doc for doc in filtered_docs if doc.get('quality_score', 0) >= args.min_quality]
    
    # 4. 计算相关性分数
    results = []
    for doc in filtered_docs:
        relevance = calculate_relevance_score(args.query, doc, search_index)
        results.append({
            "document": doc,
            "relevance_score": round(relevance, 4)
        })
    
    # 5. 排序并返回 Top-K
    results.sort(key=lambda x: (x['relevance_score'], x['document'].get('quality_score', 0)), reverse=True)
    top_results = results[:args.top_k]
    
    # 6. 格式化输出
    output = {
        "query": args.query,
        "platform": args.platform,
        "results": [
            {
                "id": item['document']['id'],
                "title": item['document']['title'],
                "platform": item['document'].get('platform', 'unknown'),
                "file_path": item['document']['file_path'],
                "relevance_score": item['relevance_score'],
                "quality_score": item['document'].get('quality_score', 0),
                "word_count": item['document'].get('word_count', 0),
                "reusable_elements": item['document'].get('reusable_elements', {})
            }
            for item in top_results
        ],
        "total_found": len(results),
        "search_time_ms": int((time.time() - start_time) * 1000)
    }
    
    # 输出 JSON 格式结果
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
