#!/usr/bin/env python3
"""
检查点管理脚本
借鉴 LangGraph 的 checkpointing 机制

使用方法:
    # 保存检查点
    python3 checkpoint_manager.py save \
        --feature-id TASK-014 \
        --checkpoint-id ckpt-014 \
        --state '{"createdFiles": ["/backend/api/auth/register.py"]}'
    
    # 恢复检查点
    python3 checkpoint_manager.py restore --checkpoint-id ckpt-014
    
    # 列出所有检查点
    python3 checkpoint_manager.py list
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List


def save_checkpoint(
    feature_id: str,
    checkpoint_id: str,
    state: Dict,
    output_dir: str = "doc/06_dev-logs"
) -> str:
    """
    保存检查点
    
    参数:
        feature_id: 功能ID（如 TASK-014）
        checkpoint_id: 检查点ID（如 ckpt-014）
        state: 状态数据（dict）
        output_dir: 输出目录
    
    返回:
        检查点文件路径
    """
    checkpoint_data = {
        "checkpointId": checkpoint_id,
        "featureId": feature_id,
        "timestamp": datetime.now().isoformat(),
        "state": state
    }
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 保存检查点文件
    checkpoint_file = output_path / f"checkpoint_{checkpoint_id}.json"
    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
    
    # 同时更新 feature_list.json 中对应功能的 checkpoint 字段
    feature_list_path = output_path / "feature_list.json"
    if feature_list_path.exists():
        try:
            with open(feature_list_path, 'r', encoding='utf-8') as f:
                feature_list = json.load(f)
            
            # 查找并更新对应功能
            for phase in feature_list.get("phases", []):
                for feature in phase.get("features", []):
                    if feature.get("featureId") == feature_id:
                        feature["checkpoint"] = {
                            "checkpointId": checkpoint_id,
                            "timestamp": checkpoint_data["timestamp"],
                            "state": state
                        }
                        break
            
            # 保存更新后的 feature_list.json
            with open(feature_list_path, 'w', encoding='utf-8') as f:
                json.dump(feature_list, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  无法更新 feature_list.json: {e}", file=sys.stderr)
    
    return str(checkpoint_file)


def restore_checkpoint(checkpoint_id: str, input_dir: str = "doc/06_dev-logs") -> Dict:
    """
    恢复检查点
    
    参数:
        checkpoint_id: 检查点ID
        input_dir: 输入目录
    
    返回:
        检查点数据
    """
    checkpoint_file = Path(input_dir) / f"checkpoint_{checkpoint_id}.json"
    
    if not checkpoint_file.exists():
        raise FileNotFoundError(f"检查点不存在：{checkpoint_file}")
    
    with open(checkpoint_file, 'r', encoding='utf-8') as f:
        checkpoint_data = json.load(f)
    
    return checkpoint_data


def list_checkpoints(input_dir: str = "doc/06_dev-logs") -> List[Dict]:
    """
    列出所有检查点
    
    参数:
        input_dir: 输入目录
    
    返回:
        检查点列表
    """
    checkpoints = []
    input_path = Path(input_dir)
    
    if not input_path.exists():
        return checkpoints
    
    for checkpoint_file in input_path.glob("checkpoint_*.json"):
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
                checkpoints.append({
                    "checkpointId": checkpoint_data.get("checkpointId"),
                    "featureId": checkpoint_data.get("featureId"),
                    "timestamp": checkpoint_data.get("timestamp"),
                    "file": str(checkpoint_file)
                })
        except:
            continue
    
    # 按时间排序
    checkpoints.sort(key=lambda x: x["timestamp"], reverse=True)
    return checkpoints


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="检查点管理")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # save 命令
    save_parser = subparsers.add_parser("save", help="保存检查点")
    save_parser.add_argument("--feature-id", required=True, help="功能ID")
    save_parser.add_argument("--checkpoint-id", required=True, help="检查点ID")
    save_parser.add_argument("--state", required=True, help="状态数据（JSON 字符串）")
    save_parser.add_argument("--output-dir", default="doc/06_dev-logs", help="输出目录")
    
    # restore 命令
    restore_parser = subparsers.add_parser("restore", help="恢复检查点")
    restore_parser.add_argument("--checkpoint-id", required=True, help="检查点ID")
    restore_parser.add_argument("--input-dir", default="doc/06_dev-logs", help="输入目录")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出所有检查点")
    list_parser.add_argument("--input-dir", default="doc/06_dev-logs", help="输入目录")
    
    args = parser.parse_args()
    
    if args.command == "save":
        # 解析状态 JSON
        try:
            state = json.loads(args.state)
        except json.JSONDecodeError as e:
            print(f"❌ 状态数据格式错误：{e}", file=sys.stderr)
            sys.exit(1)
        
        # 保存检查点
        checkpoint_file = save_checkpoint(
            feature_id=args.feature_id,
            checkpoint_id=args.checkpoint_id,
            state=state,
            output_dir=args.output_dir
        )
        print(f"✅ 检查点已保存：{checkpoint_file}")
    
    elif args.command == "restore":
        # 恢复检查点
        try:
            checkpoint_data = restore_checkpoint(args.checkpoint_id, args.input_dir)
            print(json.dumps(checkpoint_data, indent=2, ensure_ascii=False))
            print(f"\n✅ 检查点已恢复：{args.checkpoint_id}", file=sys.stderr)
        except FileNotFoundError as e:
            print(f"❌ {e}", file=sys.stderr)
            sys.exit(1)
    
    elif args.command == "list":
        # 列出检查点
        checkpoints = list_checkpoints(args.input_dir)
        if checkpoints:
            print(f"📋 找到 {len(checkpoints)} 个检查点：\n", file=sys.stderr)
            for cp in checkpoints:
                print(f"  - {cp['checkpointId']} ({cp['featureId']}) - {cp['timestamp']}")
        else:
            print("📋 未找到检查点", file=sys.stderr)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
