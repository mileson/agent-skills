#!/usr/bin/env python3
"""
Config Checker - 图床配置检查器

功能：
1. 检查配置文件是否存在
2. 验证必需字段是否填写
3. 返回 JSON 结果供 AI 决策

使用：
    python check_config.py [config_path]

返回格式：
{
  "config_exists": true,
  "config_path": "~/.cursor/skills/markdown-image-uploader/config/image_hosts.yaml",
  "is_valid": true,
  "active_provider": "aliyun_oss",
  "missing_fields": [],
  "recommendation": {
    "action": "ready" | "create_config" | "fill_config",
    "message": "配置完整，可以开始上传"
  }
}
"""

import json
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, List


def check_config(config_path: str = None) -> Dict[str, Any]:
    """
    检查配置文件
    
    Args:
        config_path: 配置文件路径（默认：config/image_hosts.yaml）
    
    Returns:
        检测结果字典
    """
    # 默认配置路径
    if config_path is None:
        skill_dir = Path(__file__).parent.parent
        config_path = skill_dir / "config" / "image_hosts.yaml"
    else:
        config_path = Path(config_path)
    
    result = {
        "config_exists": False,
        "config_path": str(config_path),
        "is_valid": False,
        "active_provider": None,
        "missing_fields": [],
        "recommendation": {
            "action": "create_config",
            "message": "配置文件不存在，请创建配置"
        }
    }
    
    # 检查文件是否存在
    if not config_path.exists():
        return result
    
    result["config_exists"] = True
    
    # 读取配置
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        result["recommendation"] = {
            "action": "fix_config",
            "message": f"配置文件格式错误：{str(e)}"
        }
        return result
    
    # 检查 active_provider
    active_provider = config.get('active_provider', 'aliyun_oss')
    result["active_provider"] = active_provider
    
    # 检查提供商配置
    if active_provider == 'aliyun_oss':
        provider_config = config.get('aliyun_oss', {})
        required_fields = [
            'access_key_id',
            'access_key_secret',
            'bucket',
            'region',
            'endpoint'
        ]
        
        missing = []
        for field in required_fields:
            value = provider_config.get(field, '')
            # 检查是否为空或为模板值
            if not value or value.startswith('你的'):
                missing.append(field)
        
        result["missing_fields"] = missing
        
        if missing:
            result["recommendation"] = {
                "action": "fill_config",
                "message": f"请填写以下必需字段：{', '.join(missing)}"
            }
        else:
            result["is_valid"] = True
            result["recommendation"] = {
                "action": "ready",
                "message": "配置完整，可以开始上传"
            }
    
    else:
        result["recommendation"] = {
            "action": "unsupported",
            "message": f"不支持的提供商：{active_provider}"
        }
    
    return result


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="图床配置检查器")
    parser.add_argument(
        "config_path",
        nargs="?",
        default=None,
        help="配置文件路径（默认：config/image_hosts.yaml）"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出 JSON 格式（供 AI 读取）"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="美化 JSON 输出"
    )
    
    args = parser.parse_args()
    
    # 检查配置
    result = check_config(args.config_path)
    
    if args.json:
        # JSON 格式输出
        indent = 2 if args.pretty else None
        print(json.dumps(result, indent=indent, ensure_ascii=False))
    
    else:
        # 人类可读格式
        print("🔍 配置检查结果")
        print("=" * 50)
        print(f"📄 配置文件: {result['config_path']}")
        print(f"✅ 文件存在: {result['config_exists']}")
        
        if result['config_exists']:
            print(f"🔧 活跃提供商: {result['active_provider']}")
            print(f"✓ 配置有效: {result['is_valid']}")
            
            if result['missing_fields']:
                print(f"⚠️  缺少字段: {', '.join(result['missing_fields'])}")
        
        print()
        print(f"💡 推荐操作: {result['recommendation']['action']}")
        print(f"   {result['recommendation']['message']}")


if __name__ == "__main__":
    main()
