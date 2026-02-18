#!/usr/bin/env python3
# ============================================================
# 文件说明书 (File Manual)
# ============================================================
# 核心功能 (Core Function)
# 通过 GitHub API 创建新仓库，凭证从 secrets-vault 读取。
#
# 输入 (Input)
# - 命令行参数: --name, --description, --private, --gitignore
#
# 输出 (Output)
# - stdout: JSON 格式的仓库信息
# - exit code: 0=成功, 1=错误
#
# 定位 (Position)
# feature-development skill 阶段4 部署流程的一部分。
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


def get_secret(namespace: str, key: str = None) -> str:
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


def create_github_repo(name: str, description: str = "", private: bool = True,
                       gitignore_template: str = None) -> dict:
    """创建 GitHub 仓库"""

    # 获取凭证
    github_creds = get_secret("github")
    token = github_creds.get("token")
    username = github_creds.get("username")

    if not token:
        print("Error: GitHub token not found in secrets-vault", file=sys.stderr)
        sys.exit(1)

    # 构建 API 请求
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    data = {
        "name": name,
        "description": description,
        "private": private,
        "auto_init": False
    }
    if gitignore_template:
        data["gitignore_template"] = gitignore_template

    # 发送请求
    try:
        import requests
    except ImportError:
        print("Error: requests not installed. Run: pip install requests", file=sys.stderr)
        sys.exit(1)

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        repo_info = response.json()
        return {
            "success": True,
            "repo_id": repo_info.get("id"),
            "name": repo_info.get("name"),
            "full_name": repo_info.get("full_name"),
            "html_url": repo_info.get("html_url"),
            "clone_url": repo_info.get("clone_url"),
            "ssh_url": repo_info.get("ssh_url"),
            "private": repo_info.get("private")
        }
    elif response.status_code == 422:
        error = response.json()
        return {
            "success": False,
            "error": "Repository already exists",
            "details": error
        }
    else:
        return {
            "success": False,
            "error": f"GitHub API error: {response.status_code}",
            "details": response.text
        }


def main():
    parser = argparse.ArgumentParser(description="Create a GitHub repository")
    parser.add_argument("--name", required=True, help="Repository name")
    parser.add_argument("--description", default="", help="Repository description")
    parser.add_argument("--private", action="store_true", default=True, help="Create as private repo")
    parser.add_argument("--public", action="store_true", help="Create as public repo")
    parser.add_argument("--gitignore", help="Gitignore template (e.g., Node, Python)")

    args = parser.parse_args()

    # 处理 public/private 参数
    private = not args.public

    result = create_github_repo(
        name=args.name,
        description=args.description,
        private=private,
        gitignore_template=args.gitignore
    )

    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
