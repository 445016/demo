#!/bin/bash

set -e

echo "=================================================="
echo "  职能沟通翻译助手 - 自动安装脚本"
echo "=================================================="
echo ""

# 检测 conda
USE_CONDA=false
if command -v conda &> /dev/null; then
    echo "📌 检测到 Conda 环境管理器"
    read -p "是否使用 Conda 创建环境？(Y/n): " use_conda_choice
    use_conda_choice=${use_conda_choice:-Y}
    if [[ "$use_conda_choice" =~ ^[Yy]$ ]]; then
        USE_CONDA=true
    fi
    echo ""
fi

if [ "$USE_CONDA" = true ]; then
    # 使用 Conda
    ENV_NAME="comm-translator"
    
    echo "📌 使用 Conda 创建环境..."
    if conda env list | grep -q "^${ENV_NAME} "; then
        echo "⚠️  Conda 环境 '${ENV_NAME}' 已存在"
        read -p "是否删除并重新创建？(y/N): " recreate
        recreate=${recreate:-N}
        if [[ "$recreate" =~ ^[Yy]$ ]]; then
            conda env remove -n ${ENV_NAME} -y
            conda create -n ${ENV_NAME} python=3.11 -y
            echo "✅ Conda 环境重新创建成功"
        else
            echo "⚠️  使用现有环境"
        fi
    else
        conda create -n ${ENV_NAME} python=3.11 -y
        echo "✅ Conda 环境创建成功"
    fi
    echo ""
    
    echo "📌 激活 Conda 环境..."
    eval "$(conda shell.bash hook)"
    conda activate ${ENV_NAME}
    echo "✅ Conda 环境已激活: ${ENV_NAME}"
    echo ""
    
    echo "📌 安装依赖包..."
    pip install --upgrade pip -q
    pip install -r requirements.txt
    echo "✅ 依赖包安装完成"
    echo ""
    
else
    # 使用 venv
    echo "📌 检查 Python 版本..."
    if command -v python3.11 &> /dev/null; then
        PYTHON_CMD=python3.11
    elif command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | awk '{print $2}')
        MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 11 ]; then
            PYTHON_CMD=python3
        else
            echo "❌ 错误：需要 Python 3.11 或更高版本"
            echo "   当前版本：$PYTHON_VERSION"
            echo "   请先安装 Python 3.11+"
            exit 1
        fi
    else
        echo "❌ 错误：未找到 Python"
        echo "   请先安装 Python 3.11+"
        exit 1
    fi
    
    echo "✅ 找到 Python: $($PYTHON_CMD --version)"
    echo ""
    
    echo "📌 创建虚拟环境..."
    if [ -d "venv" ]; then
        echo "⚠️  虚拟环境已存在，跳过创建"
    else
        $PYTHON_CMD -m venv venv
        echo "✅ 虚拟环境创建成功"
    fi
    echo ""
    
    echo "📌 激活虚拟环境..."
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
    echo ""
    
    echo "📌 安装依赖包..."
    pip install --upgrade pip -q
    pip install -r requirements.txt
    echo "✅ 依赖包安装完成"
    echo ""
fi

# 配置文件
echo "📌 配置环境变量..."
if [ -f ".env" ]; then
    echo "⚠️  .env 文件已存在，跳过创建"
    echo "   如需重新配置，请手动编辑 .env 文件"
else
    cp config.example.env .env
    echo "✅ 已创建 .env 配置文件"
    echo ""
    echo "⚠️  重要：请配置 LLM API Key"
    echo "   1. 打开 .env 文件"
    echo "   2. 填入您的 API Key 和配置"
    echo ""
    echo "配置示例："
    echo "  llm_api_key=your_api_key_here"
    echo "  llm_base_url=https://open.bigmodel.cn/api/anthropic"
    echo "  llm_model=GLM-4.6"
    echo ""
    read -p "按回车键继续编辑 .env 文件，或按 Ctrl+C 退出..." 
    ${EDITOR:-nano} .env
fi
echo ""

# 完成
echo "=================================================="
echo "  ✅ 安装完成！"
echo "=================================================="
echo ""
if [ "$USE_CONDA" = true ]; then
    echo "启动服务："
    echo "  conda activate ${ENV_NAME}"
    echo "  python main.py"
else
    echo "启动服务："
    echo "  source venv/bin/activate"
    echo "  python main.py"
fi
echo ""
echo "或直接运行："
echo "  ./start.sh"
echo ""
echo "访问地址："
echo "  http://localhost:8000"
echo ""
echo "=================================================="
