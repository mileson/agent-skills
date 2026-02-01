#!/bin/bash
# Markdown to WeChat 转换器快捷脚本

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$SCRIPT_DIR/venv"
PYTHON_BIN="$VENV_DIR/bin/python"

# 检查虚拟环境是否存在
if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 首次使用，正在创建虚拟环境..."
    python3 -m venv "$VENV_DIR"
    
    echo "📦 安装依赖包..."
    "$VENV_DIR/bin/pip" install -q -r "$SCRIPT_DIR/requirements.txt"
    
    echo "✅ 环境准备完成！"
    echo ""
fi

# 检查依赖是否已安装
if ! "$PYTHON_BIN" -c "import mistune" 2>/dev/null; then
    echo "📦 检测到依赖缺失，正在安装..."
    "$VENV_DIR/bin/pip" install -q -r "$SCRIPT_DIR/requirements.txt"
    echo "✅ 依赖安装完成！"
    echo ""
fi

# 运行转换脚本
"$PYTHON_BIN" "$SCRIPT_DIR/scripts/cli.py" "$@"
