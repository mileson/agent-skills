#!/usr/bin/env python3
# ============================================================
# 文件说明书 (File Manual)
# ============================================================
# 核心功能 (Core Function)
# 从 secrets-vault/data/vault.yaml 读取指定命名空间的凭证，以 JSON 格式输出到 stdout。
#
# 输入 (Input)
# - 命令行参数: namespace（必需）、key（可选，指定字段名）
# - 数据文件: ~/.claude/skills/secrets-vault/data/vault.yaml
#
# 输出 (Output)
# - stdout: JSON 格式的凭证数据（供其他脚本 subprocess 调用并 json.loads 解析）
# - stderr: 错误信息（不影响 stdout 的 JSON 解析）
# - exit code: 0=成功, 1=错误
#
# 定位 (Position)
# secrets-vault skill 的核心读取入口，被所有需要凭证的外部 skill 调用。
#
# 依赖 (Dependency)
# - PyYAML (pyyaml): 解析 vault.yaml
# - Python 3.6+ 标准库: json, sys, pathlib
#
# 维护规则 (Maintenance Rules)
# 1. 每次修改代码逻辑后，必须检查并更新上述信息。
# 2. 禁止修改或删除本【维护规则】章节的内容。
# ============================================================

import json
import sys
from pathlib import Path

# vault.yaml 位于 skill 目录的 data 子目录
VAULT_PATH = Path(__file__).parent.parent / "data" / "vault.yaml"


def load_vault():
    """Load vault.yaml and return as dict."""
    if not VAULT_PATH.exists():
        print(
            f"Error: Vault not found at {VAULT_PATH}. "
            f"Run manage_secrets.py init first.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        import yaml
    except ImportError:
        print(
            "Error: pyyaml not installed. Run: pip install pyyaml",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(VAULT_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        return {}
    return data


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: get_secret.py <namespace> [key]\n"
            "  namespace  Service namespace in vault.yaml (e.g. github, vercel, supabase)\n"
            "  key        Optional specific field to retrieve",
            file=sys.stderr,
        )
        sys.exit(1)

    namespace = sys.argv[1]
    key = sys.argv[2] if len(sys.argv) > 2 else None

    vault = load_vault()

    if namespace not in vault:
        print(
            f"Error: Namespace '{namespace}' not found in vault. "
            f"Available: {', '.join(vault.keys()) if vault else '(empty)'}",
            file=sys.stderr,
        )
        sys.exit(1)

    entry = vault[namespace]

    if key:
        if not isinstance(entry, dict):
            print(
                f"Error: Namespace '{namespace}' is not a dict, cannot get key '{key}'.",
                file=sys.stderr,
            )
            sys.exit(1)
        if key not in entry:
            print(
                f"Error: Key '{key}' not found in namespace '{namespace}'. "
                f"Available keys: {', '.join(entry.keys())}",
                file=sys.stderr,
            )
            sys.exit(1)
        # Output single value: string for scalar, JSON for dict/list
        value = entry[key]
        if isinstance(value, (dict, list)):
            print(json.dumps(value, ensure_ascii=False))
        else:
            print(str(value))
    else:
        # Output entire namespace as JSON
        if isinstance(entry, dict):
            print(json.dumps(entry, ensure_ascii=False))
        else:
            print(json.dumps({"value": entry}, ensure_ascii=False))


if __name__ == "__main__":
    main()
