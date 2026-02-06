#!/usr/bin/env python3
# ============================================================
# 文件说明书 (File Manual)
# ============================================================
# 核心功能 (Core Function)
# 内容发布调度器入口，根据平台参数分发到对应的平台发布器。
#
# 输入 (Input)
# - 命令行参数: --platform, --workspace, --action, --auto-publish 等
#
# 输出 (Output)
# - stdout: JSON 格式的发布结果
# - 更新 metadata.yaml 中的 publish_records
#
# 定位 (Position)
# content-publisher skill 的统一入口脚本，Agent 和用户均通过此脚本操作。
#
# 依赖 (Dependency)
# - platforms/base.py: PlatformPublisher 基类
# - platforms/wechat.py: 微信公众号发布器（Phase 1）
# - platforms/xhs.py: 小红书占位（Phase 2）
# - platforms/zhihu.py: 知乎占位（Phase 2）
# - secrets-vault skill: 获取平台凭证
#
# 维护规则 (Maintenance Rules)
# 1. 每次修改代码逻辑后，必须检查并更新上述信息。
# 2. 禁止修改或删除本【维护规则】章节的内容。
# ============================================================

import argparse
import json
import sys
import os

# Add parent directory to path for package imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from platforms.wechat import WeChatPublisher
from platforms.xhs import XHSPublisher
from platforms.zhihu import ZhihuPublisher

PLATFORM_MAP = {
    "wechat": WeChatPublisher,
    "xhs": XHSPublisher,
    "zhihu": ZhihuPublisher,
}

SUPPORTED_PLATFORMS = list(PLATFORM_MAP.keys())


def cmd_publish(args):
    """Execute publish workflow."""
    platform_id = args.platform
    workspace = args.workspace

    if platform_id not in PLATFORM_MAP:
        print(
            json.dumps({
                "status": "error",
                "message": f"Unknown platform: {platform_id}. "
                           f"Supported: {', '.join(SUPPORTED_PLATFORMS)}"
            }, ensure_ascii=False),
        )
        sys.exit(1)

    publisher_cls = PLATFORM_MAP[platform_id]
    publisher = publisher_cls(workspace)

    try:
        result = publisher.full_publish_flow(auto_publish=args.auto_publish)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    except NotImplementedError as e:
        print(json.dumps({
            "status": "error",
            "message": str(e),
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": f"Publish failed: {e}",
        }, ensure_ascii=False, indent=2))
        sys.exit(1)


def cmd_status(args):
    """Check publish status."""
    platform_id = args.platform
    workspace = args.workspace

    if platform_id not in PLATFORM_MAP:
        print(f"Unknown platform: {platform_id}", file=sys.stderr)
        sys.exit(1)

    publisher_cls = PLATFORM_MAP[platform_id]
    publisher = publisher_cls(workspace)

    try:
        publisher.authenticate()
        result = publisher.get_status(args.publish_id)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": f"Status check failed: {e}",
        }, ensure_ascii=False, indent=2))
        sys.exit(1)


def cmd_list_platforms(args):
    """List supported platforms and their status."""
    print("Supported platforms:\n")
    status_map = {
        "wechat": ("✅", "可用 (Phase 1)"),
        "xhs": ("🔜", "开发中 (Phase 2)"),
        "zhihu": ("🔜", "开发中 (Phase 2)"),
    }
    for pid in SUPPORTED_PLATFORMS:
        icon, status = status_map.get(pid, ("❓", "未知"))
        cls = PLATFORM_MAP[pid]
        print(f"  {icon} {pid:10s} {cls.platform_name:10s} {status}")


def main():
    parser = argparse.ArgumentParser(
        description="Content Publisher - Multi-platform content publishing tool"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # publish command
    pub_parser = subparsers.add_parser("publish", help="Publish content to a platform")
    pub_parser.add_argument("--platform", "-p", required=True, choices=SUPPORTED_PLATFORMS)
    pub_parser.add_argument("--workspace", "-w", required=True, help="Workspace directory path")
    pub_parser.add_argument(
        "--auto-publish", action="store_true",
        help="Automatically publish after creating draft (default: draft only)"
    )
    pub_parser.set_defaults(func=cmd_publish)

    # status command
    status_parser = subparsers.add_parser("status", help="Check publish status")
    status_parser.add_argument("--platform", "-p", required=True, choices=SUPPORTED_PLATFORMS)
    status_parser.add_argument("--workspace", "-w", required=True, help="Workspace directory path")
    status_parser.add_argument("--publish-id", required=True, help="Publish task ID")
    status_parser.set_defaults(func=cmd_status)

    # list command
    list_parser = subparsers.add_parser("list", help="List supported platforms")
    list_parser.set_defaults(func=cmd_list_platforms)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
