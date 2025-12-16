# 测试套件说明

本项目使用 `pytest` 作为测试框架，包含单元测试和集成测试。

---

## 📦 安装测试依赖

```bash
# 安装所有依赖（包括测试依赖）
pip install -r requirements.txt
```

---

## 🧪 运行测试

### 运行所有测试

```bash
pytest
```

### 运行特定测试文件

```bash
# 测试 Prompt 组装服务
pytest tests/test_skill_service.py

# 测试 LLM 服务
pytest tests/test_llm_service.py

# 测试 API 端点
pytest tests/test_api.py

# 测试配置
pytest tests/test_config.py

# 测试数据模型
pytest tests/test_models.py
```

### 运行特定测试类或测试函数

```bash
# 运行特定测试类
pytest tests/test_skill_service.py::TestSkillService

# 运行特定测试函数
pytest tests/test_skill_service.py::TestSkillService::test_read_classifier_skill
```

### 使用标记运行测试

```bash
# 只运行单元测试（不运行集成测试）
pytest -m "not integration"

# 只运行集成测试（需要真实的 LLM API）
RUN_INTEGRATION_TESTS=1 pytest -m integration

# 运行慢速测试
pytest -m slow
```

### 查看详细输出

```bash
# 显示 print 输出
pytest -s

# 显示更详细的输出
pytest -vv

# 显示失败测试的完整 traceback
pytest --tb=long
```

### 生成覆盖率报告

```bash
# 生成覆盖率报告
pytest --cov=app --cov-report=html

# 查看 HTML 报告
open htmlcov/index.html  # macOS
# 或
xdg-open htmlcov/index.html  # Linux
```

---

## 📁 测试文件结构

```
tests/
├── __init__.py                  # 测试套件初始化
├── conftest.py                  # Pytest 配置和 Fixtures
├── README.md                    # 本文件
│
├── test_skill_service.py        # Prompt 组装服务测试
│   ├── TestSkillService
│   │   ├── test_read_classifier_skill
│   │   ├── test_read_translator_skill_pm_to_dev
│   │   ├── test_read_translator_skill_dev_to_pm
│   │   ├── test_invalid_skill_name
│   │   └── ...
│   └── ...
│
├── test_llm_service.py          # LLM 服务测试
│   ├── TestClassifyInput
│   │   ├── test_classify_product_requirement
│   │   ├── test_classify_technical_solution
│   │   └── test_classify_insufficient_info
│   ├── TestTranslateStream
│   │   ├── test_translate_stream_basic
│   │   └── ...
│   └── TestLLMServiceIntegration  # 集成测试
│       ├── test_real_classify
│       └── test_real_translate
│
├── test_api.py                  # API 端点测试
│   ├── TestHealthEndpoint
│   ├── TestClassifyEndpoint
│   ├── TestTranslateEndpoint
│   ├── TestCORS
│   └── TestAPIIntegration  # 集成测试
│
├── test_config.py               # 配置管理测试
│   ├── TestSettings
│   ├── TestConfigModule
│   ├── TestEnvironmentVariables
│   └── TestConfigPaths
│
└── test_models.py               # 数据模型测试
    ├── TestClassifyRequest
    ├── TestTranslateRequest
    ├── TestClassificationResult
    └── TestModelInteraction
```

---

## 🔧 Fixtures 说明

在 `conftest.py` 中定义了以下 Fixtures：

### `test_env`
设置测试环境变量（API Key、模型名称等）

### `client`
FastAPI 测试客户端，用于测试 API 端点

### `sample_pm_input`
示例产品需求输入

```python
"我们需要一个用户登录功能，支持手机号和邮箱两种方式"
```

### `sample_dev_input`
示例技术方案输入

```python
"我们对数据库查询进行了优化，使用了 Redis 缓存和索引优化，QPS 从 1000 提升到了 1300"
```

### `sample_short_input`
示例短输入（信息不足）

```python
"做一个功能"
```

### `sample_mixed_input`
示例混合话题输入

```python
"我们需要登录功能、支付功能、还有订单管理系统，性能要求 QPS 达到 5000"
```

---

## 🧩 测试类型

### 单元测试（Unit Tests）
测试单个函数或类的功能，使用 Mock 隔离外部依赖。

**特点：**
- 快速
- 不依赖外部服务（LLM API）
- 使用 `@patch` 或 `@mock` 装饰器

**示例：**
```python
@patch('app.services.llm_service.get_llm_client')
async def test_classify_product_requirement(self, mock_get_client):
    # Mock LLM 响应
    mock_client = Mock()
    # ...
```

### 集成测试（Integration Tests）
测试多个组件协同工作，需要真实的外部服务。

**特点：**
- 较慢
- 依赖真实的 LLM API
- 使用 `@pytest.mark.integration` 标记
- 需要设置环境变量 `RUN_INTEGRATION_TESTS=1`

**运行方式：**
```bash
RUN_INTEGRATION_TESTS=1 pytest -m integration
```

---

## 📊 覆盖率目标

| 模块 | 目标覆盖率 | 当前状态 |
|------|-----------|---------|
| `app/services/skill_service.py` | 90%+ | ✅ |
| `app/services/llm_service.py` | 80%+ | ✅ |
| `app/routers/api.py` | 85%+ | ✅ |
| `app/models/schemas.py` | 95%+ | ✅ |
| `config.py` | 90%+ | ✅ |

---

## 💡 编写测试的最佳实践

### 1. 使用描述性的测试名称

❌ **不好：**
```python
def test_1(self):
    ...
```

✅ **好：**
```python
def test_classify_product_requirement_returns_correct_type(self):
    ...
```

### 2. 遵循 AAA 模式

```python
def test_example(self):
    # Arrange（准备）
    request = ClassifyRequest(text="测试")
    
    # Act（执行）
    result = process_request(request)
    
    # Assert（断言）
    assert result.success == True
```

### 3. 每个测试只测试一个功能点

❌ **不好：**
```python
def test_everything(self):
    # 测试分类
    result1 = classify(...)
    assert ...
    
    # 测试翻译
    result2 = translate(...)
    assert ...
    
    # 测试配置
    config = get_config()
    assert ...
```

✅ **好：**
```python
def test_classify_returns_correct_type(self):
    result = classify(...)
    assert result.type == "产品需求"

def test_translate_returns_stream(self):
    result = translate(...)
    assert is_stream(result)
```

### 4. 使用 Fixtures 减少重复代码

```python
# conftest.py
@pytest.fixture
def sample_input():
    return "测试输入"

# test_xxx.py
def test_with_fixture(sample_input):
    result = process(sample_input)
    assert result is not None
```

### 5. 对异步函数使用 `pytest.mark.asyncio`

```python
@pytest.mark.asyncio
async def test_async_function(self):
    result = await async_function()
    assert result is not None
```

---

## 🐛 常见问题

### Q1: 测试时报错 "ModuleNotFoundError"

**A:** 确保项目根目录在 Python 路径中：
```python
# conftest.py 中已经处理
sys.path.insert(0, str(project_root))
```

### Q2: 异步测试不工作

**A:** 确保：
1. 安装了 `pytest-asyncio`
2. 使用了 `@pytest.mark.asyncio` 装饰器
3. `pytest.ini` 中设置了 `asyncio_mode = auto`

### Q3: Mock 不生效

**A:** 检查 Mock 的路径是否正确：
```python
# ❌ 错误：Mock 导入的位置
@patch('anthropic.Anthropic')

# ✅ 正确：Mock 使用的位置
@patch('app.services.llm_service.get_llm_client')
```

### Q4: 集成测试跳过

**A:** 设置环境变量：
```bash
RUN_INTEGRATION_TESTS=1 pytest -m integration
```

---

## 📚 相关资源

- [Pytest 官方文档](https://docs.pytest.org/)
- [pytest-asyncio 文档](https://pytest-asyncio.readthedocs.io/)
- [FastAPI 测试指南](https://fastapi.tiangolo.com/tutorial/testing/)
- [Python Mock 对象指南](https://docs.python.org/3/library/unittest.mock.html)

---

## 🎯 下一步

1. **提高覆盖率**：目标 90% 以上
2. **添加性能测试**：使用 `pytest-benchmark`
3. **添加 E2E 测试**：使用 Playwright 或 Selenium
4. **CI/CD 集成**：在 GitHub Actions 中运行测试

