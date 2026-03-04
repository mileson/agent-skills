#!/usr/bin/env python3
# ============================================================
# 文件说明书 (File Manual)
# ============================================================
# 核心功能 (Core Function)
# 验证 Vercel 部署状态，检查 GitHub 关联是否生效。
#
# 输入 (Input)
# - 命令行参数: --project-id, --team-id, --wait
#
# 输出 (Output)
# - stdout: JSON 格式的验证结果
# - exit code: 0=成功, 1=错误
#
# 定位 (Position)
# spec-driven-development skill 阶段4 部署验证部分。
#
# 依赖 (Dependency)
# - requests: HTTP 请求
# - secrets-vault: 凭证管理
#
# 维护规则 (Maintenance Rules)
# 1. 每次修改代码逻辑后，必须检查并更新上述信息。
# 2. 禁止修改或删除本【维护规则】章节的内容。
# ============================================================

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def get_secret(namespace: str, key: str = None):
    """从 secrets-vault 获取凭证"""
    # vault.yaml 位于 secrets-vault skill 的 data 目录
    script_path = Path(__file__).parent.parent.parent.parent / "secrets-vault" / "scripts" / "get_secret.py"
    if not script_path.exists():
        script_path = Path.home() / ".claude" / "skills" / "secrets-vault" / "scripts" / "get_secret.py"
    if not script_path.exists():
        script_path = Path.home() / ".cursor" / "skills" / "secrets-vault" / "scripts" / "get_secret.py"

    cmd = ["python3", str(script_path), namespace]
    if key:
        cmd.append(key)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: Failed to get secret '{namespace}/{key}': {result.stderr}", file=sys.stderr)
        sys.exit(1)

    if key:
        return result.stdout.strip()
    else:
        return json.loads(result.stdout)


def get_project_info(project_id: str, team_id: str = None) -> dict:
    """获取 Vercel 项目信息"""
    vercel_creds = get_secret("vercel")
    token = vercel_creds.get("token")

    if not token:
        print("Error: Vercel token not found in secrets-vault", file=sys.stderr)
        sys.exit(1)

    if not team_id:
        team_id = vercel_creds.get("team_id")

    url = f"https://api.vercel.com/v9/projects/{project_id}"
    if team_id:
        url += f"?teamId={team_id}"

    headers = {"Authorization": f"Bearer {token}"}

    try:
        import requests
    except ImportError:
        print("Error: requests not installed. Run: pip install requests", file=sys.stderr)
        sys.exit(1)

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"API error: {response.status_code}", "details": response.text}


def get_deployments(project_id: str, team_id: str = None, limit: int = 5) -> dict:
    """获取最近的部署记录"""
    vercel_creds = get_secret("vercel")
    token = vercel_creds.get("token")

    if not team_id:
        team_id = vercel_creds.get("team_id")

    url = f"https://api.vercel.com/v6/deployments?projectId={project_id}&limit={limit}"
    if team_id:
        url += f"&teamId={team_id}"

    headers = {"Authorization": f"Bearer {token}"}

    try:
        import requests
    except ImportError:
        print("Error: requests not installed. Run: pip install requests", file=sys.stderr)
        sys.exit(1)

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"API error: {response.status_code}"}


def verify_deployment(project_id: str, team_id: str = None, wait: int = 0) -> dict:
    """验证部署状态"""

    # 如果需要等待，先等待
    if wait > 0:
        print(f"Waiting {wait} seconds for deployment...", file=sys.stderr)
        time.sleep(wait)

    # 获取项目信息
    project_info = get_project_info(project_id, team_id)
    if "error" in project_info:
        return {"success": False, "error": project_info["error"]}

    link = project_info.get("link", {})

    # 获取最近的部署
    deployments_info = get_deployments(project_id, team_id)
    deployments = deployments_info.get("deployments", [])

    # 分析部署状态
    latest_github_deployment = None
    for dep in deployments:
        meta = dep.get("meta", {})
        if meta.get("githubCommitRef"):
            latest_github_deployment = {
                "state": dep.get("readyState"),
                "branch": meta.get("githubCommitRef"),
                "commit_message": meta.get("githubCommitMessage"),
                "commit_sha": meta.get("githubCommitSha"),
                "url": dep.get("url"),
                "created_at": dep.get("createdAt")
            }
            break

    return {
        "success": True,
        "project": {
            "name": project_info.get("name"),
            "id": project_info.get("id"),
            "framework": project_info.get("framework")
        },
        "github_link": {
            "connected": bool(link.get("type")),
            "type": link.get("type"),
            "repo": f"{link.get('org')}/{link.get('repo')}" if link.get("org") else None,
            "branch": link.get("productionBranch")
        },
        "latest_deployment": latest_github_deployment,
        "deployment_count": len(deployments)
    }


def main():
    parser = argparse.ArgumentParser(description="Verify Vercel deployment status")
    parser.add_argument("--project-id", required=True, help="Vercel project ID")
    parser.add_argument("--team-id", help="Vercel team ID (optional)")
    parser.add_argument("--wait", type=int, default=0, help="Wait N seconds before checking")

    args = parser.parse_args()

    result = verify_deployment(
        project_id=args.project_id,
        team_id=args.team_id,
        wait=args.wait
    )

    print(json.dumps(result, indent=2))

    # 如果 GitHub 关联成功且最新部署完成，返回成功
    if result.get("success"):
        link = result.get("github_link", {})
        latest = result.get("latest_deployment")
        if link.get("connected") and latest and latest.get("state") == "READY":
            sys.exit(0)

    sys.exit(1)


if __name__ == "__main__":
    main()
