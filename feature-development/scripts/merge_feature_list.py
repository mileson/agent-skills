#!/usr/bin/env python3
"""
合并功能清单脚本（Brownfield 模式）
将新增功能合并到现有 feature_list.json

使用方法:
    python3 merge_feature_list.py \
        --existing doc/06_dev-logs/feature_list.json \
        --new-phase-name "Phase 03: 智能推荐系统" \
        --new-version "2.0" \
        --new-features '[{"featureId": "TASK-051", "description": "推荐引擎"}]'
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict


def merge_feature_list(
    existing_path: str,
    new_phase_name: str,
    new_version: str,
    new_features: List[Dict],
    base_features: List[str] = None
) -> str:
    """
    合并新功能到现有 feature_list.json
    
    参数:
        existing_path: 现有 feature_list.json 路径
        new_phase_name: 新 Phase 名称
        new_version: 新版本号
        new_features: 新增功能列表
        base_features: 依赖的基础功能 ID 列表（可选）
    
    返回:
        合并后的 feature_list.json 路径
    """
    # 1. 读取现有功能清单
    with open(existing_path, 'r', encoding='utf-8') as f:
        existing_list = json.load(f)
    
    # 2. 备份现有文件
    backup_path = existing_path.replace(".json", f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(existing_list, f, indent=2, ensure_ascii=False)
    print(f"✅ 已备份到：{backup_path}", file=sys.stderr)
    
    # 3. 生成新的 Phase
    phase_count = len(existing_list["phases"]) + 1
    new_phase_id = f"phase-{phase_count:02d}"
    
    new_phase = {
        "phaseId": new_phase_id,
        "phaseName": new_phase_name,
        "version": new_version,
        "priority": phase_count,
        "status": "pending",
        "baseVersion": existing_list["project"].get("version", "1.0"),
        "baseFeatures": base_features or [],
        "features": new_features
    }
    
    # 4. 合并到现有 phases
    existing_list["phases"].append(new_phase)
    
    # 5. 更新 metadata
    new_feature_count = len(new_features)
    existing_list["metadata"]["totalFeatures"] = existing_list["metadata"].get("totalFeatures", 0) + new_feature_count
    
    # 重新计算 pending 数量
    pending_count = sum(
        1 for p in existing_list["phases"] 
        for f in p.get("features", []) 
        if f.get("status") == "pending"
    )
    existing_list["metadata"]["pendingFeatures"] = pending_count
    
    # 更新进度百分比
    total = existing_list["metadata"]["totalFeatures"]
    completed = existing_list["metadata"].get("completedFeatures", 0)
    existing_list["metadata"]["progressPercentage"] = round((completed / total) * 100, 1) if total > 0 else 0.0
    
    # 更新版本和时间
    existing_list["metadata"]["currentVersion"] = new_version
    existing_list["metadata"]["baseVersion"] = existing_list["project"].get("version")
    existing_list["metadata"]["lastUpdated"] = datetime.now().isoformat()
    
    # 6. 更新项目版本
    existing_list["project"]["baseVersion"] = existing_list["project"].get("version")
    existing_list["project"]["version"] = new_version
    
    # 7. 保存合并后的文件
    with open(existing_path, 'w', encoding='utf-8') as f:
        json.dump(existing_list, f, indent=2, ensure_ascii=False)
    
    return existing_path


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="合并功能清单")
    parser.add_argument("--existing", required=True, help="现有 feature_list.json 路径")
    parser.add_argument("--new-phase-name", required=True, help="新 Phase 名称")
    parser.add_argument("--new-version", required=True, help="新版本号")
    parser.add_argument("--new-features", required=True, help="新增功能列表（JSON 字符串）")
    parser.add_argument("--base-features", nargs="+", help="依赖的基础功能 ID 列表")
    
    args = parser.parse_args()
    
    # 解析新增功能
    try:
        new_features = json.loads(args.new_features)
    except json.JSONDecodeError as e:
        print(f"❌ 新增功能数据格式错误：{e}", file=sys.stderr)
        sys.exit(1)
    
    # 合并功能清单
    output_path = merge_feature_list(
        existing_path=args.existing,
        new_phase_name=args.new_phase_name,
        new_version=args.new_version,
        new_features=new_features,
        base_features=args.base_features
    )
    
    print(f"✅ 功能清单已合并：{output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
