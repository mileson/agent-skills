#!/usr/bin/env python3
"""
YAML 工具函数
用于 content-creator skill 的元数据读写操作

依赖：pip install pyyaml rich
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


def save_metadata_yaml(
    data: Dict[str, Any],
    file_path: str,
    add_timestamp: bool = True
) -> Path:
    """
    保存元数据为 YAML 格式
    
    Args:
        data: 元数据字典
        file_path: 输出文件路径
        add_timestamp: 是否添加生成时间戳
    
    Returns:
        Path: 生成的文件路径
    
    示例:
        >>> meta = {'audience': 'AI编程爱好者', 'purpose': '分享技术教程'}
        >>> save_metadata_yaml(meta, 'Output/_drafts/00_extracted_meta.yaml')
    """
    file_path = Path(file_path)
    
    # 添加生成时间戳
    if add_timestamp and 'meta' in data:
        data['meta']['generated_at'] = datetime.now().isoformat()
    
    # 确保目录存在
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 写入 YAML
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(
            data,
            f,
            allow_unicode=True,           # 支持中文
            default_flow_style=False,     # 块样式（更易读）
            sort_keys=False,              # 保持字段顺序
            indent=2,                     # 缩进 2 空格
            width=120                     # 每行最大宽度
        )
    
    print(f"✅ YAML 元数据已保存: {file_path}")
    return file_path


def load_metadata_yaml(file_path: str) -> Dict[str, Any]:
    """
    读取 YAML 元数据
    
    Args:
        file_path: YAML 文件路径
    
    Returns:
        Dict: 元数据字典
    
    Raises:
        FileNotFoundError: 文件不存在
        yaml.YAMLError: YAML 格式错误
    
    示例:
        >>> meta = load_metadata_yaml('Output/_drafts/00_extracted_meta.yaml')
        >>> print(meta['audience'])
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"YAML 文件不存在: {file_path}")
    
    # 读取 YAML
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = yaml.safe_load(f)
            print(f"✅ YAML 元数据已加载: {file_path}")
            return data or {}
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"YAML 格式错误: {e}")


def validate_metadata_yaml(file_path: str) -> tuple[bool, Optional[str]]:
    """
    验证 YAML 元数据的格式和完整性
    
    Args:
        file_path: YAML 文件路径
    
    Returns:
        tuple: (是否有效, 错误信息)
    
    示例:
        >>> is_valid, error = validate_metadata_yaml('Output/_drafts/00_extracted_meta.yaml')
        >>> if not is_valid:
        >>>     print(f"验证失败: {error}")
    """
    try:
        # 读取 YAML
        data = load_metadata_yaml(file_path)
        
        # 检查必需字段
        required_fields = [
            'audience',
            'purpose',
            'brand_voice',
            'writing_style',
            'trending_topics',
            'key_points',
            'publish_platforms'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"缺少必需字段: {', '.join(missing_fields)}"
        
        # 检查字段类型
        if not isinstance(data['trending_topics'], list):
            return False, "trending_topics 必须是列表"
        
        if not isinstance(data['key_points'], list):
            return False, "key_points 必须是列表"
        
        if not isinstance(data['publish_platforms'], list):
            return False, "publish_platforms 必须是列表"
        
        # 检查平台有效性
        valid_platforms = [
            'xhs', 'wechat', 'zhihu', 'jike', 'twitter',
            'linkedin', 'douyin', 'bilibili', 'instagram'
        ]
        invalid_platforms = [
            p for p in data['publish_platforms']
            if p not in valid_platforms
        ]
        if invalid_platforms:
            return False, f"无效的平台: {', '.join(invalid_platforms)}"
        
        print(f"✅ YAML 元数据验证通过")
        return True, None
        
    except FileNotFoundError as e:
        return False, str(e)
    except yaml.YAMLError as e:
        return False, f"YAML 格式错误: {e}"
    except Exception as e:
        return False, f"验证失败: {e}"


def display_metadata_rich(file_path: str):
    """
    使用 Rich 库美化展示 YAML 元数据
    
    Args:
        file_path: YAML 文件路径
    
    示例:
        >>> display_metadata_rich('Output/_drafts/00_extracted_meta.yaml')
    """
    try:
        from rich.console import Console
        from rich.syntax import Syntax
        from rich.panel import Panel
    except ImportError:
        print("❌ 需要安装 rich 库: pip install rich")
        return
    
    file_path = Path(file_path)
    
    # 读取 YAML 文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        yaml_content = f.read()
    
    # 创建 Rich 控制台
    console = Console()
    
    # 语法高亮
    syntax = Syntax(
        yaml_content,
        "yaml",
        theme="monokai",
        line_numbers=True,
        word_wrap=True
    )
    
    # 面板包裹
    panel = Panel(
        syntax,
        title=f"[bold cyan]📊 元数据预览[/bold cyan]",
        subtitle=f"文件: {file_path.name}",
        border_style="cyan"
    )
    
    # 打印
    console.print(panel)
    console.print("\n[dim]💡 提示: 输入 'continue' 继续，或提出修改意见[/dim]\n")


def save_workspace_config_yaml(
    data: Dict[str, Any],
    workspace_dir: str
) -> Path:
    """
    保存工作区配置为 YAML 格式
    
    Args:
        data: 工作区配置字典
        workspace_dir: 工作区目录路径
    
    Returns:
        Path: 生成的配置文件路径
    
    示例:
        >>> config = {
        >>>     'workspace': {'name': 'AI编程实战', 'created_at': '2026-02-04T10:00:00Z'},
        >>>     'target_platforms': ['xhs', 'wechat']
        >>> }
        >>> save_workspace_config_yaml(config, '/path/to/workspace')
    """
    workspace_dir = Path(workspace_dir)
    config_file = workspace_dir / 'workspace.config.yaml'
    
    # 添加最后更新时间
    if 'meta' not in data:
        data['meta'] = {}
    data['meta']['last_updated'] = datetime.now().isoformat()
    
    # 写入 YAML
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.safe_dump(
            data,
            f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
            indent=2,
            width=120
        )
    
    print(f"✅ 工作区配置已保存: {config_file}")
    return config_file


def load_workspace_config_yaml(workspace_dir: str) -> Dict[str, Any]:
    """
    读取工作区配置（智能支持 JSON 和 YAML 格式）
    
    Args:
        workspace_dir: 工作区目录路径
    
    Returns:
        Dict: 工作区配置字典
    
    Raises:
        FileNotFoundError: 配置文件不存在
    
    示例:
        >>> config = load_workspace_config_yaml('/path/to/workspace')
        >>> print(config['generation_status'])
    """
    workspace_dir = Path(workspace_dir)
    
    # 优先读取 YAML 格式
    yaml_file = workspace_dir / 'workspace.config.yaml'
    if yaml_file.exists():
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            print(f"✅ 工作区配置已加载: {yaml_file}")
            return data or {}
    
    # 向后兼容：支持 JSON 格式
    json_file = workspace_dir / 'workspace.config.json'
    if json_file.exists():
        import json
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"⚠️  检测到旧格式 JSON 配置，建议迁移至 YAML")
            print(f"✅ 工作区配置已加载: {json_file}")
            return data
    
    raise FileNotFoundError(f"工作区配置文件不存在: {workspace_dir}")


def validate_workspace_config_yaml(workspace_dir: str) -> tuple[bool, Optional[str]]:
    """
    验证工作区配置的格式和完整性
    
    Args:
        workspace_dir: 工作区目录路径
    
    Returns:
        tuple: (是否有效, 错误信息)
    
    示例:
        >>> is_valid, error = validate_workspace_config_yaml('/path/to/workspace')
        >>> if not is_valid:
        >>>     print(f"验证失败: {error}")
    """
    try:
        # 读取配置
        data = load_workspace_config_yaml(workspace_dir)
        
        # 检查必需字段
        required_fields = [
            'workspace',
            'materials',
            'target_platforms',
            'generation_status'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"缺少必需字段: {', '.join(missing_fields)}"
        
        # 检查 generation_status 有效性
        valid_statuses = [
            'initialized',
            'extraction_completed',
            'topic_selected',
            'outline_confirmed',
            'script_confirmed',
            'draft_completed',
            'scoring_completed',
            'adaptation_completed',
            'completed'
        ]
        
        if data['generation_status'] not in valid_statuses:
            return False, f"无效的 generation_status: {data['generation_status']}"
        
        print(f"✅ 工作区配置验证通过")
        return True, None
        
    except FileNotFoundError as e:
        return False, str(e)
    except Exception as e:
        return False, f"验证失败: {e}"


def convert_json_to_yaml(json_file: str, yaml_file: str) -> Path:
    """
    将 JSON 元数据转换为 YAML 格式
    
    Args:
        json_file: 输入的 JSON 文件路径
        yaml_file: 输出的 YAML 文件路径
    
    Returns:
        Path: 生成的 YAML 文件路径
    
    示例:
        >>> convert_json_to_yaml(
        >>>     'Output/_drafts/00_extracted_meta.json',
        >>>     'Output/_drafts/00_extracted_meta.yaml'
        >>> )
    """
    import json
    
    # 读取 JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 保存为 YAML
    return save_metadata_yaml(data, yaml_file)


# ==================== 命令行工具 ====================

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='YAML 元数据工具',
        epilog='示例: python yaml_utils.py validate Output/_drafts/00_extracted_meta.yaml'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 验证命令
    validate_parser = subparsers.add_parser('validate', help='验证 YAML 格式')
    validate_parser.add_argument('file', help='YAML 文件路径')
    
    # 展示命令
    display_parser = subparsers.add_parser('display', help='美化展示 YAML')
    display_parser.add_argument('file', help='YAML 文件路径')
    
    # 转换命令
    convert_parser = subparsers.add_parser('convert', help='JSON 转 YAML')
    convert_parser.add_argument('input', help='输入 JSON 文件')
    convert_parser.add_argument('output', help='输出 YAML 文件')
    
    args = parser.parse_args()
    
    if args.command == 'validate':
        is_valid, error = validate_metadata_yaml(args.file)
        if is_valid:
            print("✅ 验证通过")
        else:
            print(f"❌ 验证失败: {error}")
            exit(1)
    
    elif args.command == 'display':
        display_metadata_rich(args.file)
    
    elif args.command == 'convert':
        convert_json_to_yaml(args.input, args.output)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
