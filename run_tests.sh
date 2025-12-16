#!/bin/bash
# 测试运行脚本

set -e  # 遇到错误立即退出

echo "======================================"
echo "  职能沟通翻译助手 - 测试套件"
echo "======================================"
echo

# 检查测试依赖
echo "📦 检查测试依赖..."
python -c "import pytest" 2>/dev/null || {
    echo "❌ pytest 未安装"
    echo "   请运行: pip install -r requirements.txt"
    exit 1
}

python -c "import pytest_asyncio" 2>/dev/null || {
    echo "❌ pytest-asyncio 未安装"
    echo "   请运行: pip install -r requirements.txt"
    exit 1
}

echo "✅ 测试依赖已安装"
echo

# 运行测试
echo "🧪 运行测试套件..."
echo

if [ "$1" == "cov" ]; then
    echo "📊 运行测试并生成覆盖率报告..."
    pytest --cov=app --cov-report=html --cov-report=term
    echo
    echo "✅ 覆盖率报告已生成: htmlcov/index.html"
elif [ "$1" == "integration" ]; then
    echo "🔗 运行集成测试（需要真实的 LLM API）..."
    export RUN_INTEGRATION_TESTS=1
    pytest -m integration -v
elif [ "$1" == "fast" ]; then
    echo "⚡ 快速运行（只运行单元测试）..."
    pytest -m "not integration" --tb=short
else
    echo "🏃 运行所有测试..."
    pytest -v
fi

echo
echo "======================================"
echo "  ✅ 测试完成！"
echo "======================================"

