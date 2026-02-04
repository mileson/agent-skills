#!/usr/bin/env python3
"""
生成功能清单脚本（Greenfield 模式）
基于 PRD 和架构文档自动生成 feature_list.json

使用方法:
    python3 generate_feature_list.py \
        --project-name "电商平台" \
        --prd-path doc/01_PRD \
        --arch-path doc/02_arch \
        --output doc/06_dev-logs/feature_list.json
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict


def analyze_prd_for_features(prd_path: Path) -> List[str]:
    """
    分析 PRD 文档，提取功能点
    
    简化实现：返回占位符功能列表
    实际使用时，可以使用 NLP 分析文档内容
    """
    features = []
    
    # 读取核心流程文档
    core_flow_file = prd_path / "3_核心流程.md"
    if core_flow_file.exists():
        try:
            with open(core_flow_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 简单提取：查找列表项作为功能点
                import re
                matches = re.findall(r'^[-*]\s+(.+)$', content, re.MULTILINE)
                features.extend(matches[:20])  # 最多提取 20 个
        except:
            pass
    
    return features if features else ["功能1", "功能2", "功能3"]


def generate_feature_list(
    project_name: str,
    prd_path: str,
    arch_path: str,
    template_path: str = None
) -> Dict:
    """
    生成功能清单
    
    参数:
        project_name: 项目名称
        prd_path: PRD 目录路径
        arch_path: 架构文档目录路径
        template_path: 模板路径（可选）
    
    返回:
        feature_list 数据
    """
    # 如果提供了模板，加载模板
    if template_path and Path(template_path).exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            feature_list = json.load(f)
        
        # 更新项目信息
        feature_list["project"]["name"] = project_name
        feature_list["project"]["createdAt"] = datetime.now().isoformat()
        feature_list["metadata"]["lastUpdated"] = datetime.now().isoformat()
        
        return feature_list
    
    # 否则生成默认结构
    return {
        "project": {
            "name": project_name,
            "version": "1.0.0",
            "createdAt": datetime.now().isoformat()
        },
        "phases": [
            {
                "phaseId": "phase-01",
                "phaseName": "Phase 01: 基础环境搭建",
                "priority": 1,
                "status": "pending",
                "features": [
                    {
                        "featureId": "TASK-001",
                        "category": "infrastructure",
                        "description": "初始化项目结构",
                        "steps": [
                            "创建前端项目目录",
                            "创建后端项目目录",
                            "配置 git 仓库"
                        ],
                        "status": "pending",
                        "assignedAgent": "initializer",
                        "dependencies": [],
                        "estimatedEffort": "0.5 day",
                        "checkpoint": None
                    }
                ]
            }
        ],
        "metadata": {
            "totalFeatures": 1,
            "completedFeatures": 0,
            "progressPercentage": 0.0,
            "lastUpdated": datetime.now().isoformat()
        }
    }


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="生成功能清单")
    parser.add_argument("--project-name", required=True, help="项目名称")
    parser.add_argument("--prd-path", required=True, help="PRD 目录路径")
    parser.add_argument("--arch-path", required=True, help="架构文档目录路径")
    parser.add_argument("--template", help="模板文件路径（可选）")
    parser.add_argument("--output", required=True, help="输出文件路径")
    
    args = parser.parse_args()
    
    # 生成功能清单
    feature_list = generate_feature_list(
        project_name=args.project_name,
        prd_path=args.prd_path,
        arch_path=args.arch_path,
        template_path=args.template
    )
    
    # 保存到文件
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(feature_list, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 功能清单已生成：{output_path}", file=sys.stderr)
    print(f"   总功能数：{feature_list['metadata']['totalFeatures']}", file=sys.stderr)


if __name__ == "__main__":
    main()
