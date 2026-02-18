#!/usr/bin/env python3
# ============================================================
# 文件说明书 (File Manual)
# ============================================================
# 核心功能 (Core Function)
# 管理 secrets-vault/data/vault.yaml 的凭证数据：初始化、列出、查看（脱敏）、设置、删除。
#
# 输入 (Input)
# - 命令行参数: action + 相关参数
# - 数据文件: ~/.claude/skills/secrets-vault/data/vault.yaml
#
# 输出 (Output)
# - stdout: 操作结果（人类可读格式）
# - 文件写入: vault.yaml 的增删改
#
# 定位 (Position)
# secrets-vault skill 的管理入口，由用户或 Agent 执行凭证管理操作。
#
# 依赖 (Dependency)
# - PyYAML (pyyaml): 读写 vault.yaml
# - Python 3.6+ 标准库: sys, pathlib, os
#
# 维护规则 (Maintenance Rules)
# 1. 每次修改代码逻辑后，必须检查并更新上述信息。
# 2. 禁止修改或删除本【维护规则】章节的内容。
# ============================================================

import os
import sys
from pathlib import Path

# 路径相对于脚本位置
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
DATA_DIR = SKILL_DIR / "data"
VAULT_PATH = DATA_DIR / "vault.yaml"
VAULT_EXAMPLE_PATH = SKILL_DIR / "vault.yaml.example"

VAULT_TEMPLATE = """\
# ============================================================
# secrets-vault: 通用敏感信息保险库
# ============================================================
# 顶层 key = 服务命名空间（自由定义，随用随加）
# 其他 skill 通过 get_secret.py <namespace> [key] 读取
#
# 命名空间命名规范:
#   github       - GitHub Token
#   vercel       - Vercel API Token
#   supabase     - Supabase 凭证
#   x_oauth      - X/Twitter OAuth
#   wechat_mp    - 微信公众号凭证
#   openai       - OpenAI API
#   personal     - 个人信息
# ============================================================

# ---- GitHub (必需) ----
# 用于创建仓库、推送代码、关联 Vercel
github:
  token: "ghp_your_github_token"
  username: "your_username"
  default_visibility: "private"

# ---- Vercel (前端部署) ----
# 用于关联 GitHub、自动部署
vercel:
  token: "your_vercel_token"
  team_id: "team_xxxx"  # 可选

# ---- Supabase (后端部署) ----
# 用于数据库、认证、存储
supabase:
  project_id: "your_project_id"
  url: "https://xxxx.supabase.co"
  anon_key: "eyJhbGci..."
  service_role_key: "eyJhbGci..."
  database_url: "postgresql://..."

# ---- X/Twitter OAuth ----
# 用于 X 登录集成
x_oauth:
  client_id: "your_client_id"
  client_secret: "your_client_secret"
  callback_url: "https://your-app.com/api/auth/callback/x"

# ---- 微信公众号 (可选) ----
# wechat_mp:
#   app_id: "your_app_id"
#   app_secret: "your_app_secret"

# ---- 个人信息 (可选) ----
# personal:
#   name: "你的名字"
#   email: "you@example.com"
"""


def ensure_yaml():
    try:
        import yaml  # noqa: F401
        return True
    except ImportError:
        print("Error: pyyaml not installed. Run: pip install pyyaml", file=sys.stderr)
        return False


def load_vault():
    if not VAULT_PATH.exists():
        return {}
    import yaml
    with open(VAULT_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if data else {}


def save_vault(data):
    import yaml
    with open(VAULT_PATH, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def mask_value(value):
    """Mask sensitive values for display."""
    s = str(value)
    if len(s) <= 4:
        return "****"
    return s[:3] + "*" * (len(s) - 6) + s[-3:] if len(s) > 6 else s[:2] + "****"


def cmd_init():
    """Initialize the vault directory and template file."""
    if VAULT_PATH.exists():
        print(f"Vault already exists at {VAULT_PATH}")
        print("Use 'set' command to add entries.")
        return

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(str(DATA_DIR), 0o700)

    with open(VAULT_PATH, "w", encoding="utf-8") as f:
        f.write(VAULT_TEMPLATE)
    os.chmod(str(VAULT_PATH), 0o600)

    print(f"✅ Vault initialized at {VAULT_PATH}")
    print(f"   Directory permissions: 700 (owner only)")
    print(f"   File permissions: 600 (owner read/write)")
    print(f"\nNext: Edit {VAULT_PATH} to add your credentials,")
    print(f"  or use: manage_secrets.py set <namespace> <key> <value>")


def cmd_list():
    """List all namespaces in the vault."""
    vault = load_vault()
    if not vault:
        print("Vault is empty. Use 'set' to add entries.")
        return

    print(f"📦 Vault namespaces ({len(vault)}):\n")
    for ns, data in vault.items():
        if isinstance(data, dict):
            keys = ", ".join(data.keys())
            print(f"  {ns}:")
            for k, v in data.items():
                print(f"    {k}: {mask_value(v)}")
        else:
            print(f"  {ns}: {mask_value(data)}")
        print()


def cmd_get(namespace):
    """Show a namespace's contents (masked)."""
    vault = load_vault()
    if namespace not in vault:
        print(f"Error: Namespace '{namespace}' not found.", file=sys.stderr)
        print(f"Available: {', '.join(vault.keys()) if vault else '(empty)'}", file=sys.stderr)
        sys.exit(1)

    entry = vault[namespace]
    print(f"📦 {namespace}:")
    if isinstance(entry, dict):
        for k, v in entry.items():
            print(f"  {k}: {mask_value(v)}")
    else:
        print(f"  value: {mask_value(entry)}")


def cmd_set(namespace, key, value):
    """Set a key-value pair in a namespace."""
    vault = load_vault()

    if namespace not in vault:
        vault[namespace] = {}
    elif not isinstance(vault[namespace], dict):
        vault[namespace] = {"value": vault[namespace]}

    vault[namespace][key] = value
    save_vault(vault)
    print(f"✅ Set {namespace}.{key} = {mask_value(value)}")


def cmd_remove(namespace):
    """Remove a namespace from the vault."""
    vault = load_vault()
    if namespace not in vault:
        print(f"Error: Namespace '{namespace}' not found.", file=sys.stderr)
        sys.exit(1)

    del vault[namespace]
    save_vault(vault)
    print(f"✅ Removed namespace '{namespace}'")


def cmd_remove_key(namespace, key):
    """Remove a specific key from a namespace."""
    vault = load_vault()
    if namespace not in vault:
        print(f"Error: Namespace '{namespace}' not found.", file=sys.stderr)
        sys.exit(1)

    entry = vault[namespace]
    if not isinstance(entry, dict) or key not in entry:
        print(f"Error: Key '{key}' not found in '{namespace}'.", file=sys.stderr)
        sys.exit(1)

    del entry[key]
    if not entry:
        del vault[namespace]
        print(f"✅ Removed key '{key}' from '{namespace}' (namespace now empty, removed)")
    else:
        save_vault(vault)
        print(f"✅ Removed key '{key}' from '{namespace}'")

    save_vault(vault)


def main():
    usage = (
        "Usage: manage_secrets.py <action> [args]\n\n"
        "Actions:\n"
        "  init                          Initialize vault (data/vault.yaml)\n"
        "  list                          List all namespaces (masked values)\n"
        "  get <namespace>               Show namespace contents (masked)\n"
        "  set <namespace> <key> <value> Set a key-value pair\n"
        "  remove <namespace>            Remove entire namespace\n"
        "  remove-key <namespace> <key>  Remove a specific key\n"
    )

    if len(sys.argv) < 2:
        print(usage, file=sys.stderr)
        sys.exit(1)

    action = sys.argv[1]

    if action == "init":
        cmd_init()
    elif action in ("list", "ls"):
        if not ensure_yaml():
            sys.exit(1)
        cmd_list()
    elif action == "get":
        if len(sys.argv) < 3:
            print("Usage: manage_secrets.py get <namespace>", file=sys.stderr)
            sys.exit(1)
        if not ensure_yaml():
            sys.exit(1)
        cmd_get(sys.argv[2])
    elif action == "set":
        if len(sys.argv) < 5:
            print("Usage: manage_secrets.py set <namespace> <key> <value>", file=sys.stderr)
            sys.exit(1)
        if not ensure_yaml():
            sys.exit(1)
        # Join remaining args as value (in case value has spaces)
        value = " ".join(sys.argv[4:])
        cmd_set(sys.argv[2], sys.argv[3], value)
    elif action == "remove":
        if len(sys.argv) < 3:
            print("Usage: manage_secrets.py remove <namespace>", file=sys.stderr)
            sys.exit(1)
        if not ensure_yaml():
            sys.exit(1)
        cmd_remove(sys.argv[2])
    elif action == "remove-key":
        if len(sys.argv) < 4:
            print("Usage: manage_secrets.py remove-key <namespace> <key>", file=sys.stderr)
            sys.exit(1)
        if not ensure_yaml():
            sys.exit(1)
        cmd_remove_key(sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown action: {action}\n", file=sys.stderr)
        print(usage, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
