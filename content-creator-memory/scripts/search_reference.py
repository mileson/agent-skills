#!/usr/bin/env python3
"""
搜索标杆案例 - Search Reference

功能：基于查询词和过滤条件检索标杆案例（reference_examples）

用法：
    python3 search_reference.py \\
        --query "查询词" \\
        --filters "field:value,field:value" \\
        --top-k 3

示例：
    python3 search_reference.py \\
        --query "标题钩子技巧" \\
        --filters "platform:wechat,author:AI产品黄叔" \\
        --top-k 2
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional


def load_reference_data(output_dir: str) -> tuple:
    """加载标杆案例数据"""
    try:
        output_path = Path(output_dir).expanduser()
        
        # 加载标杆案例索引
        with open(output_path / "reference_examples.json", 'r', encoding='utf-8') as f:
            references = json.load(f)
        
        # 加载搜索索引
        with open(output_path / "search_index.json", 'r', encoding='utf-8') as f:
            search_index = json.load(f)
        
        return references, search_index
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
    
    # 1. 标题匹配（权重：50%）
    title = doc.get('title', '').lower()
    if query_lower in title:
        score += 0.5
    
    # 2. 关键词匹配（权重：30%）
    keywords = doc.get('keywords', [])
    for keyword in keywords:
        if query_lower in keyword.lower() or keyword.lower() in query_lower:
            score += 0.3 / len(keywords) if keywords else 0
    
    # 3. TF-IDF 匹配（权重：20%）
    doc_id = doc.get('id')
    tfidf_scores = search_index.get('tfidf_scores', {}).get(doc_id, {})
    
    for keyword in query.split():
        if keyword.lower() in tfidf_scores:
            score += tfidf_scores[keyword.lower()] * 0.2
    
    return min(1.0, score)


def search_reference(query: str, filters: Dict[str, str], top_k: int, output_dir: str) -> Dict[str, Any]:
    """搜索标杆案例的主函数"""
    start_time = time.time()
    
    # 1. 加载数据
    references, search_index = load_reference_data(output_dir)
    
    # 2. 应用过滤条件
    filtered = apply_filters(references, filters)
    
    # 3. 计算相关度分数
    results = []
    for doc in filtered:
        relevance = calculate_relevance_score(query, doc, search_index)
        results.append({
            "document": doc,
            "relevance_score": round(relevance, 4)
        })
    
    # 4. 排序并返回 Top-K
    results.sort(key=lambda x: x['relevance_score'], reverse=True)
    top_results = results[:top_k]
    
    # 5. 格式化输出
    output = {
        "results": [
            {
                "id": item['document']['id'],
                "title": item['document']['title'],
                "author": item['document'].get('author', ''),
                "file_path": item['document']['file_path'],
                "relevance_score": item['relevance_score'],
                "title_hooks": item['document'].get('title_hooks', []),
                "structural_patterns": item['document'].get('structural_patterns', []),
                "expression_techniques": item['document'].get('expression_techniques', [])
            }
            for item in top_results
        ],
        "total_found": len(results),
        "search_time_ms": int((time.time() - start_time) * 1000)
    }
    
    return output


def main():
    parser = argparse.ArgumentParser(description='搜索标杆案例')
    parser.add_argument('--query', required=True, help='搜索查询词')
    parser.add_argument('--filters', help='过滤条件（格式：field:value,field:value）')
    parser.add_argument('--top-k', type=int, default=3, help='返回结果数量（默认：3）')
    parser.add_argument('--output-dir', default='~/.cursor/skills/content-creator-memory/data', 
                        help='索引数据目录路径')
    
    args = parser.parse_args()
    
    filters = parse_filters(args.filters)
    result = search_reference(args.query, filters, args.top_k, args.output_dir)
    
    # 输出 JSON 格式结果
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
