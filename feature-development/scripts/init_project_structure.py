#!/usr/bin/env python3
"""
初始化项目文档结构（Greenfield 模式）

使用方法:
    python3 init_project_structure.py --project-name "电商平台" --output-dir doc/
"""

import os
import sys
from pathlib import Path
from datetime import datetime


def create_directory_structure(base_path: Path):
    """创建完整的文档目录结构"""
    directories = [
        "01_PRD",
        "02_arch",
        "03_database",
        "04_api",
        "05_implementation",
        "06_dev-logs",
        "06_dev-logs/errors",
        "07_testing"
    ]
    
    for dir_name in directories:
        dir_path = base_path / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)


def create_readme_files(base_path: Path):
    """为每个目录创建 README.md"""
    readme_content = {
        "01_PRD": "# 产品需求文档\n\n本目录包含产品需求的详细说明。\n",
        "02_arch": "# 架构设计文档\n\n本目录包含技术选型、系统架构和交互时序图。\n",
        "03_database": "# 数据库设计文档\n\n本目录包含数据表设计、建表SQL和索引设计。\n",
        "04_api": "# API 接口文档\n\n本目录包含 RESTful API 设计和错误码定义。\n",
        "05_implementation": "# 实现细节文档\n\n本目录包含核心模块的详细设计。\n",
        "06_dev-logs": "# 开发日志\n\n本目录包含开发进度、功能清单和检查点。\n",
        "07_testing": "# 测试文档\n\n本目录包含测试策略和测试用例。\n"
    }
    
    for dir_name, content in readme_content.items():
        readme_path = base_path / dir_name / "README.md"
        if not readme_path.exists():
            readme_path.write_text(content, encoding="utf-8")


def create_doc_standard(base_path: Path, project_name: str):
    """创建文档规范文件"""
    content = f"""# 文档规范

**项目名称**: {project_name}
**创建时间**: {datetime.now().strftime("%Y-%m-%d")}

## 文档编写原则

1. **清晰性**: 使用清晰的标题和章节结构
2. **完整性**: 包含所有必要的信息
3. **可维护性**: 易于更新和维护
4. **版本管理**: 使用文档修订历史表格

## Mermaid 图表规范

所有 Mermaid 图表必须包含样式头：

```mermaid
%%{{init: {{ 'theme': 'base', 'themeVariables': {{ 'primaryColor': '#e3f2fd', 'primaryBorderColor': '#1565c0' }} }} }}%%
graph TB
    A[开始] --> B[结束]
```

## 表格规范

表格行之间严禁空行，保证渲染正常。

## 文档修订历史

每个文档必须包含修订历史表格：

| 版本 | 日期 | 修订人 | 修订内容 |
|------|------|--------|----------|
| v1.0 | {datetime.now().strftime("%Y-%m-%d")} | AI Agent | 初始版本 |
"""
    
    standard_path = base_path / "00_文档规范.md"
    standard_path.write_text(content, encoding="utf-8")


def init_project_structure(project_name: str, output_dir: str):
    """
    初始化项目文档结构
    
    参数:
        project_name: 项目名称
        output_dir: 输出目录路径
    """
    base_path = Path(output_dir)
    base_path.mkdir(parents=True, exist_ok=True)
    
    # 创建目录结构
    create_directory_structure(base_path)
    print(f"✅ 目录结构已创建", file=sys.stderr)
    
    # 创建 README 文件
    create_readme_files(base_path)
    print(f"✅ README 文件已创建", file=sys.stderr)
    
    # 创建文档规范
    create_doc_standard(base_path, project_name)
    print(f"✅ 文档规范已创建", file=sys.stderr)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="初始化项目文档结构")
    parser.add_argument("--project-name", required=True, help="项目名称")
    parser.add_argument("--output-dir", default="doc", help="输出目录路径")
    
    args = parser.parse_args()
    
    # 初始化结构
    init_project_structure(args.project_name, args.output_dir)
    
    print(f"\n✅ 项目文档结构初始化完成：{args.output_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()
