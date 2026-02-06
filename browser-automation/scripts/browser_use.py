#!/usr/bin/env python3
"""
Browser-Use Cloud API 客户端脚本
用于执行 AI 驱动的浏览器自动化任务

用法:
    python browser_use.py create <task> [options]
    python browser_use.py run <task> [options]     # 创建并等待完成
    python browser_use.py status <task_id>
    python browser_use.py list [options]
    python browser_use.py stop <task_id>
    python browser_use.py download <task_id> <file_id>
"""

import argparse
import json
import os
import subprocess
import sys
import time


# ============ 配置 ============
API_BASE = "https://api.browser-use.com/api/v2"
API_KEY = "bu_n2UbZT1TaNcP8dFF33OY63XLVfYxjzHP8Uz1PtoMG8k"

# 任务状态
STATUS_STARTED = "started"
STATUS_PAUSED = "paused"
STATUS_FINISHED = "finished"
STATUS_STOPPED = "stopped"

TERMINAL_STATUSES = {STATUS_FINISHED, STATUS_STOPPED}


# ============ API 函数 ============
def _get_headers():
    return [
        "-H", f"X-Browser-Use-API-Key: {API_KEY}",
        "-H", "Content-Type: application/json",
    ]


def _request(method: str, path: str, body: dict = None) -> dict:
    """发送 HTTP 请求 (使用 curl)"""
    url = f"{API_BASE}{path}"
    cmd = ["curl", "-s", "-X", method] + _get_headers()

    if body:
        cmd.extend(["-d", json.dumps(body)])

    cmd.append(url)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise RuntimeError(f"curl 错误: {result.stderr}")

        response = json.loads(result.stdout)
        if "error" in response:
            raise RuntimeError(f"API 错误: {response}")
        return response
    except subprocess.TimeoutExpired:
        raise TimeoutError("请求超时")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JSON 解析错误: {result.stdout}") from e


def create_task(
    task: str,
    session_id: str = None,
    allowed_domains: list = None,
    max_steps: int = None,
    vision: bool = None,
    flash_mode: bool = None,
    thinking: bool = None,
) -> dict:
    """创建浏览器自动化任务"""
    body = {"task": task}

    if session_id:
        body["sessionId"] = session_id
    if allowed_domains:
        body["allowedDomains"] = allowed_domains
    if max_steps:
        body["maxSteps"] = max_steps
    if vision is not None:
        body["vision"] = vision
    if flash_mode:
        body["flashMode"] = flash_mode
    if thinking is not None:
        body["thinking"] = thinking

    return _request("POST", "/tasks", body)


def get_task(task_id: str) -> dict:
    """获取任务详情"""
    return _request("GET", f"/tasks/{task_id}")


def list_tasks(
    page_size: int = 20,
    page_number: int = 1,
    session_id: str = None,
    status: str = None,
) -> dict:
    """列出任务"""
    params = [f"pageSize={page_size}", f"pageNumber={page_number}"]
    if session_id:
        params.append(f"sessionId={session_id}")
    if status:
        params.append(f"filterBy={status}")

    return _request("GET", f"/tasks?{'&'.join(params)}")


def stop_task(task_id: str, action: str = "stop") -> dict:
    """停止/暂停/恢复任务"""
    return _request("PATCH", f"/tasks/{task_id}", {"action": action})


def get_download_url(task_id: str, file_id: str) -> dict:
    """获取文件下载链接"""
    return _request("GET", f"/files/tasks/{task_id}/output-files/{file_id}")


def wait_for_task(task_id: str, poll_interval: float = 3.0, timeout: float = 300) -> dict:
    """轮询等待任务完成"""
    start_time = time.time()

    while True:
        task = get_task(task_id)
        status = task.get("status", "")

        if status in TERMINAL_STATUSES:
            return task

        elapsed = time.time() - start_time
        if elapsed > timeout:
            raise TimeoutError(f"任务超时 ({timeout}s)，当前状态: {status}")

        time.sleep(poll_interval)


def run_task(task: str, **options) -> dict:
    """创建任务并等待完成"""
    created = create_task(task, **options)
    task_id = created.get("id")

    if not task_id:
        raise RuntimeError(f"创建任务失败: {created}")

    return wait_for_task(task_id)


# ============ CLI ============
def cmd_create(args):
    result = create_task(
        task=args.task,
        session_id=args.session_id,
        allowed_domains=args.allowed_domains.split(",") if args.allowed_domains else None,
        max_steps=args.max_steps,
        vision=args.vision,
        flash_mode=args.flash_mode,
        thinking=args.thinking,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_run(args):
    result = run_task(
        task=args.task,
        session_id=args.session_id,
        allowed_domains=args.allowed_domains.split(",") if args.allowed_domains else None,
        max_steps=args.max_steps,
        vision=args.vision,
        flash_mode=args.flash_mode,
        thinking=args.thinking,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_status(args):
    result = get_task(args.task_id)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_list(args):
    result = list_tasks(
        page_size=args.page_size,
        page_number=args.page_number,
        session_id=args.session_id,
        status=args.status,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_stop(args):
    result = stop_task(args.task_id, args.action)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_download(args):
    result = get_download_url(args.task_id, args.file_id)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Browser-Use Cloud API CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create 命令
    p_create = subparsers.add_parser("create", help="创建任务")
    p_create.add_argument("task", help="任务描述")
    p_create.add_argument("--session-id", help="会话 ID")
    p_create.add_argument("--allowed-domains", help="允许的域名 (逗号分隔)")
    p_create.add_argument("--max-steps", type=int, help="最大步骤数")
    p_create.add_argument("--vision", action="store_true", help="启用视觉")
    p_create.add_argument("--flash-mode", action="store_true", help="快速模式")
    p_create.add_argument("--thinking", action="store_true", help="启用思考")
    p_create.set_defaults(func=cmd_create)

    # run 命令 (创建并等待)
    p_run = subparsers.add_parser("run", help="创建任务并等待完成")
    p_run.add_argument("task", help="任务描述")
    p_run.add_argument("--session-id", help="会话 ID")
    p_run.add_argument("--allowed-domains", help="允许的域名 (逗号分隔)")
    p_run.add_argument("--max-steps", type=int, help="最大步骤数")
    p_run.add_argument("--vision", action="store_true", help="启用视觉")
    p_run.add_argument("--flash-mode", action="store_true", help="快速模式")
    p_run.add_argument("--thinking", action="store_true", help="启用思考")
    p_run.set_defaults(func=cmd_run)

    # status 命令
    p_status = subparsers.add_parser("status", help="获取任务状态")
    p_status.add_argument("task_id", help="任务 ID")
    p_status.set_defaults(func=cmd_status)

    # list 命令
    p_list = subparsers.add_parser("list", help="列出任务")
    p_list.add_argument("--page-size", type=int, default=20)
    p_list.add_argument("--page-number", type=int, default=1)
    p_list.add_argument("--session-id", help="按会话筛选")
    p_list.add_argument("--status", help="按状态筛选")
    p_list.set_defaults(func=cmd_list)

    # stop 命令
    p_stop = subparsers.add_parser("stop", help="控制任务执行")
    p_stop.add_argument("task_id", help="任务 ID")
    p_stop.add_argument("--action", choices=["stop", "pause", "resume"], default="stop")
    p_stop.set_defaults(func=cmd_stop)

    # download 命令
    p_dl = subparsers.add_parser("download", help="获取文件下载链接")
    p_dl.add_argument("task_id", help="任务 ID")
    p_dl.add_argument("file_id", help="文件 ID")
    p_dl.set_defaults(func=cmd_download)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
