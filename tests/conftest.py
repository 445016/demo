"""
Pytest 配置和 Fixtures
"""
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# 添加项目根目录到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_env():
    """设置测试环境变量"""
    os.environ["llm_api_key"] = "test_key"
    os.environ["llm_base_url"] = "https://test.example.com"
    os.environ["llm_model"] = "test-model"
    os.environ["log_level"] = "ERROR"  # 测试时降低日志级别
    yield
    # 清理


@pytest.fixture
def client(test_env):
    """FastAPI 测试客户端"""
    from main import app
    return TestClient(app)


@pytest.fixture
def sample_pm_input():
    """示例产品需求输入"""
    return "我们需要一个用户登录功能，支持手机号和邮箱两种方式"


@pytest.fixture
def sample_dev_input():
    """示例技术方案输入"""
    return "我们对数据库查询进行了优化，使用了 Redis 缓存和索引优化，QPS 从 1000 提升到了 1300"


@pytest.fixture
def sample_short_input():
    """示例短输入（信息不足）"""
    return "做一个功能"


@pytest.fixture
def sample_mixed_input():
    """示例混合话题输入"""
    return "我们需要登录功能、支付功能、还有订单管理系统，性能要求 QPS 达到 5000"

