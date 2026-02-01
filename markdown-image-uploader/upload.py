#!/usr/bin/env python3
"""
Markdown Image Uploader - 包装脚本

解决 Python 相对导入问题的包装器
"""

import sys
from pathlib import Path

# 将 scripts 目录添加到 Python 路径
SCRIPT_DIR = Path(__file__).parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

# 导入 CLI 模块并执行
if __name__ == "__main__":
    # 动态导入避免相对导入问题
    import importlib.util
    
    cli_path = SCRIPT_DIR / "cli.py"
    spec = importlib.util.spec_from_file_location("cli", cli_path)
    cli_module = importlib.util.module_from_spec(spec)
    
    # 设置模块的 __package__
    cli_module.__package__ = "scripts"
    
    spec.loader.exec_module(cli_module)
    
    # 执行 main 函数
    cli_module.main()
