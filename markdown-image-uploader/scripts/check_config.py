#!/usr/bin/env python3
"""
Config Checker - 图床配置检查器

功能：
1. 检查配置文件是否存在
2. 验证必需字段是否填写
3. 返回 JSON 结果供 AI 决策
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict

import yaml

PLACEHOLDER_PREFIXES = ('你的', 'your-', 'replace-me', 'example-')
REQUIRED_FIELDS = ['access_key_id', 'access_key_secret', 'bucket', 'region', 'endpoint']


def is_placeholder(value: Any) -> bool:
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    text = value.strip()
    if not text:
        return True
    return text.lower().startswith(PLACEHOLDER_PREFIXES)


def read_secret_namespace(namespace: str):
    candidates = [
        Path(__file__).resolve().parents[2] / 'secrets-vault' / 'scripts' / 'get_secret.py',
        Path.home() / '.cursor' / 'skills' / 'secrets-vault' / 'scripts' / 'get_secret.py',
        Path.home() / '.claude' / 'skills' / 'secrets-vault' / 'scripts' / 'get_secret.py',
    ]
    for script in candidates:
        if not script.exists():
            continue
        result = subprocess.run(['python3', str(script), namespace], capture_output=True, text=True)
        if result.returncode != 0:
            continue
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            continue
    return None


def resolve_config_path(config_path: str = None) -> Path:
    if config_path is not None:
        return Path(config_path)
    skill_dir = Path(__file__).parent.parent
    my_hosts = skill_dir / 'config' / 'my_hosts.yaml'
    image_hosts = skill_dir / 'config' / 'image_hosts.yaml'
    return my_hosts if my_hosts.exists() else image_hosts


def merge_vault(provider_config: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(provider_config)
    if not any(is_placeholder(merged.get(field)) for field in REQUIRED_FIELDS):
        return merged
    vault_data = read_secret_namespace('aliyun_oss')
    if not isinstance(vault_data, dict):
        return merged
    for field in REQUIRED_FIELDS:
        if is_placeholder(merged.get(field)) and vault_data.get(field):
            merged[field] = vault_data[field]
    return merged


def check_config(config_path: str = None) -> Dict[str, Any]:
    config_path = resolve_config_path(config_path)
    result = {
        'config_exists': False,
        'config_path': str(config_path),
        'is_valid': False,
        'active_provider': None,
        'missing_fields': [],
        'credential_source': 'config_file',
        'recommendation': {
            'action': 'create_config',
            'message': '配置文件不存在，请创建配置'
        }
    }

    if not config_path.exists():
        vault_data = read_secret_namespace('aliyun_oss')
        if isinstance(vault_data, dict) and all(vault_data.get(field) for field in REQUIRED_FIELDS):
            result.update({
                'config_exists': False,
                'is_valid': True,
                'active_provider': 'aliyun_oss',
                'credential_source': 'secrets_vault',
                'recommendation': {
                    'action': 'ready',
                    'message': '未找到本地 my_hosts.yaml，但 secrets-vault 中的 aliyun_oss 配置完整。'
                }
            })
        return result

    result['config_exists'] = True

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
    except Exception as e:
        result['recommendation'] = {
            'action': 'fix_config',
            'message': f'配置文件格式错误：{str(e)}'
        }
        return result

    active_provider = config.get('active_provider', 'aliyun_oss')
    result['active_provider'] = active_provider

    if active_provider != 'aliyun_oss':
        result['recommendation'] = {
            'action': 'unsupported',
            'message': f'不支持的提供商：{active_provider}'
        }
        return result

    provider_config = merge_vault(config.get('aliyun_oss', {}))
    missing = [field for field in REQUIRED_FIELDS if is_placeholder(provider_config.get(field))]
    result['missing_fields'] = missing
    result['credential_source'] = 'secrets_vault' if not missing and read_secret_namespace('aliyun_oss') else 'config_file'

    if missing:
        result['recommendation'] = {
            'action': 'fill_config',
            'message': f"请填写以下必需字段：{', '.join(missing)}"
        }
    else:
        result['is_valid'] = True
        result['recommendation'] = {
            'action': 'ready',
            'message': '配置完整，可以开始上传'
        }

    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description='图床配置检查器')
    parser.add_argument('config_path', nargs='?', default=None, help='配置文件路径（默认优先 config/my_hosts.yaml，其次 config/image_hosts.yaml）')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式（供 AI 读取）')
    parser.add_argument('--pretty', action='store_true', help='美化 JSON 输出')
    args = parser.parse_args()

    result = check_config(args.config_path)

    if args.json:
        indent = 2 if args.pretty else None
        print(json.dumps(result, indent=indent, ensure_ascii=False))
    else:
        print('🔍 配置检查结果')
        print('=' * 50)
        print(f"📄 配置文件: {result['config_path']}")
        print(f"✅ 文件存在: {result['config_exists']}")
        print(f"🔐 凭证来源: {result['credential_source']}")

        if result['active_provider']:
            print(f"🔧 活跃提供商: {result['active_provider']}")
            print(f"✓ 配置有效: {result['is_valid']}")
        if result['missing_fields']:
            print(f"⚠️  缺少字段: {', '.join(result['missing_fields'])}")

        print()
        print(f"💡 推荐操作: {result['recommendation']['action']}")
        print(f"   {result['recommendation']['message']}")


if __name__ == '__main__':
    main()
