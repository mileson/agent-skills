#!/usr/bin/env python3
"""
错误处理脚本：生成 JSON 格式的结构化错误日志
借鉴 nn-gene 的错误处理机制

使用方法:
    python3 handle_agent_error.py \
        --project-name "项目名称" \
        --feature-id "TASK-014" \
        --error-message "错误描述" \
        --agent-session "coding-agent-session-5"
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def generate_error_log(
    project_name: str,
    feature_id: str,
    error_message: str,
    agent_session: str,
    stack_trace: Optional[str] = None,
    last_command: Optional[str] = None,
    working_directory: Optional[str] = None,
    open_files: Optional[list] = None,
    output_dir: str = "Documentation/DevLogs/errors"
) -> str:
    """
    生成结构化的错误日志
    
    参数:
        project_name: 项目名称
        feature_id: 功能ID
        error_message: 错误消息
        agent_session: Agent 会话ID
        stack_trace: 堆栈跟踪（可选）
        last_command: 最后执行的命令（可选）
        working_directory: 工作目录（可选）
        open_files: 打开的文件列表（可选）
        output_dir: 输出目录
    
    返回:
        错误日志文件路径
    """
    error_details = {
        "ProjectName": project_name,
        "FeatureId": feature_id,
        "FailedAt": datetime.now().isoformat(),
        "ErrorMessage": error_message,
        "AgentSession": agent_session,
        "StackTrace": stack_trace or "N/A",
        "ContextState": {
            "lastCommand": last_command or "N/A",
            "workingDirectory": working_directory or ".",
            "openFiles": open_files or []
        }
    }
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    error_file = output_path / f"error_{timestamp}.json"
    
    # 保存到文件
    with open(error_file, "w", encoding="utf-8") as f:
        json.dump(error_details, f, indent=2, ensure_ascii=False)
    
    return str(error_file)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="生成错误日志")
    parser.add_argument("--project-name", required=True, help="项目名称")
    parser.add_argument("--feature-id", required=True, help="功能ID")
    parser.add_argument("--error-message", required=True, help="错误消息")
    parser.add_argument("--agent-session", required=True, help="Agent 会话ID")
    parser.add_argument("--stack-trace", help="堆栈跟踪")
    parser.add_argument("--last-command", help="最后执行的命令")
    parser.add_argument("--working-directory", help="工作目录")
    parser.add_argument("--open-files", nargs="+", help="打开的文件列表")
    parser.add_argument("--output-dir", default="Documentation/DevLogs/errors", help="输出目录")
    
    args = parser.parse_args()
    
    # 生成错误日志
    error_file = generate_error_log(
        project_name=args.project_name,
        feature_id=args.feature_id,
        error_message=args.error_message,
        agent_session=args.agent_session,
        stack_trace=args.stack_trace,
        last_command=args.last_command,
        working_directory=args.working_directory,
        open_files=args.open_files,
        output_dir=args.output_dir
    )
    
    print(f"✅ 错误日志已生成：{error_file}", file=sys.stderr)
    print(error_file)


if __name__ == "__main__":
    main()
