#!/usr/bin/env python3
# ============================================================
# 文件说明书 (File Manual)
# ============================================================
# 核心功能 (Core Function)
# 通过 Vercel API 将 GitHub 仓库关联到 Vercel 项目，凭证从 secrets-vault 读取。
#
# 输入 (Input)
# - 命令行参数: --project-id, --repo, --branch, --team-id
#
# 输出 (Output)
# - stdout: JSON 格式的关联结果
# - exit code: 0=成功, 1=错误
#
# 定位 (Position)
# spec-driven-development skill 阶段4 部署流程的一部分。
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


def link_vercel_github(project_id: str, repo: str, branch: str = "main",
                       team_id: str = None) -> dict:
    """关联 GitHub 仓库到 Vercel 项目"""

    # 获取凭证
    vercel_creds = get_secret("vercel")
    token = vercel_creds.get("token")

    if not token:
        print("Error: Vercel token not found in secrets-vault", file=sys.stderr)
        sys.exit(1)

    if not team_id:
        team_id = vercel_creds.get("team_id")

    # 构建 API 请求
    url = f"https://api.vercel.com/v9/projects/{project_id}/link"
    if team_id:
        url += f"?teamId={team_id}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "type": "github",
        "repo": repo,
        "branch": branch
    }

    # 发送请求
    try:
        import requests
    except ImportError:
        print("Error: requests not installed. Run: pip install requests", file=sys.stderr)
        sys.exit(1)

    response = requests.post(url, headers=headers, json=data)

    if response.status_code in [200, 201]:
        project_info = response.json()
        link = project_info.get("link", {})
        return {
            "success": True,
            "link": {
                "type": link.get("type"),
                "repo": link.get("repo"),
                "org": link.get("org"),
                "production_branch": link.get("productionBranch"),
                "repo_id": link.get("repoId")
            },
            "project_name": project_info.get("name")
        }
    else:
        error_info = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
        return {
            "success": False,
            "error": f"Vercel API error: {response.status_code}",
            "details": error_info.get("error", {}).get("message", response.text)
        }


def main():
    parser = argparse.ArgumentParser(description="Link GitHub repo to Vercel project")
    parser.add_argument("--project-id", required=True, help="Vercel project ID")
    parser.add_argument("--repo", required=True, help="GitHub repo (owner/repo)")
    parser.add_argument("--branch", default="main", help="Production branch")
    parser.add_argument("--team-id", help="Vercel team ID (optional)")

    args = parser.parse_args()

    result = link_vercel_github(
        project_id=args.project_id,
        repo=args.repo,
        branch=args.branch,
        team_id=args.team_id
    )

    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
