#!/bin/bash

set -e

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "❌ 错误：配置文件 .env 不存在"
    echo "   请先运行 ./install.sh 安装"
    exit 1
fi

# 检测使用 conda 还是 venv
if command -v conda &> /dev/null && conda env list | grep -q "^comm-translator "; then
    # 使用 Conda
    echo "📌 检测到 Conda 环境"
    eval "$(conda shell.bash hook)"
    conda activate comm-translator
    echo "✅ Conda 环境已激活: comm-translator"
elif [ -d "venv" ]; then
    # 使用 venv
    echo "📌 检测到虚拟环境"
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
else
    echo "❌ 错误：未找到虚拟环境或 Conda 环境"
    echo "   请先运行 ./install.sh 安装"
    exit 1
fi

# 启动服务
echo "🚀 启动服务..."
python main.py
