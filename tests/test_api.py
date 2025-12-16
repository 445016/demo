"""
测试 API 端点
"""
import pytest
from unittest.mock import patch, Mock, AsyncMock
import json


class TestHealthEndpoint:
    """测试健康检查端点"""
    
    def test_health_check(self, client):
        """测试健康检查接口"""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data


class TestClassifyEndpoint:
    """测试分类端点"""
    
    @patch('app.routers.api.classify_input')
    def test_classify_success(self, mock_classify, client, sample_pm_input):
        """测试成功的分类请求"""
        # Mock 分类结果
        from app.models.schemas import ClassificationResult
        mock_result = ClassificationResult(
            type="产品需求",
            confidence=0.95,
            reasoning="包含功能需求和用户视角",
            keywords=["用户", "登录", "功能"],
            action="translate"
        )
        
        # 将 AsyncMock 的返回值设置为 mock_result
        mock_classify.return_value = mock_result
        
        # 发送请求
        response = client.post(
            "/api/classify",
            json={"text": sample_pm_input}
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "产品需求"
        assert data["confidence"] == 0.95
        assert data["action"] == "translate"
    
    def test_classify_empty_text(self, client):
        """测试空文本分类"""
        response = client.post(
            "/api/classify",
            json={"text": ""}
        )
        
        # 应该返回 422 (Validation Error)
        assert response.status_code == 422
    
    def test_classify_invalid_json(self, client):
        """测试无效的 JSON"""
        response = client.post(
            "/api/classify",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422


class TestTranslateEndpoint:
    """测试翻译端点"""
    
    @patch('app.routers.api.translate_stream')
    @patch('app.routers.api.classify_input')
    def test_translate_auto_mode(self, mock_classify, mock_translate, client, sample_pm_input):
        """测试自动识别模式的翻译"""
        # Mock 分类结果
        from app.models.schemas import ClassificationResult
        mock_classify_result = ClassificationResult(
            type="产品需求",
            confidence=0.95,
            reasoning="包含功能需求",
            keywords=["登录", "功能"],
            action="translate"
        )
        
        # 设置 AsyncMock
        mock_classify.return_value = mock_classify_result
        
        # Mock 翻译流
        async def mock_stream(*args, **kwargs):
            yield "[理解确认]\n"
            yield "我理解您的需求...\n"
        
        mock_translate.return_value = mock_stream()
        
        # 发送请求（不指定 source_role 和 target_role）
        response = client.post(
            "/api/translate",
            json={"text": sample_pm_input}
        )
        
        # 验证响应
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    
    @patch('app.routers.api.translate_stream')
    def test_translate_manual_mode(self, mock_translate, client, sample_pm_input):
        """测试手动指定模式的翻译"""
        # Mock 翻译流
        async def mock_stream(*args, **kwargs):
            yield "[理解确认]\n"
            yield "我理解您的需求...\n"
        
        mock_translate.return_value = mock_stream()
        
        # 发送请求（指定 source_role 和 target_role）
        response = client.post(
            "/api/translate",
            json={
                "text": sample_pm_input,
                "source_role": "pm",
                "target_role": "dev"
            }
        )
        
        # 验证响应
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    
    def test_translate_short_input(self, client):
        """测试输入过短"""
        response = client.post(
            "/api/translate",
            json={"text": "短"}
        )
        
        # 应该返回 400 (输入过短)
        assert response.status_code == 400
    
    @patch('app.routers.api.classify_input')
    def test_translate_clarify_action(self, mock_classify, client, sample_short_input):
        """测试需要澄清的情况"""
        # Mock 分类结果（action = clarify）
        from app.models.schemas import ClassificationResult
        mock_classify_result = ClassificationResult(
            type="不明确",
            confidence=0.45,
            reasoning="信息不足",
            keywords=["功能"],
            action="clarify"
        )
        
        mock_classify.return_value = mock_classify_result
        
        # 发送请求
        response = client.post(
            "/api/translate",
            json={"text": sample_short_input}
        )
        
        # 验证响应
        assert response.status_code == 200
        # SSE 响应应该包含澄清提示


class TestCORS:
    """测试 CORS 配置"""
    
    def test_cors_headers(self, client):
        """测试 CORS 头部"""
        response = client.options(
            "/api/health",
            headers={"Origin": "http://localhost:3000"}
        )
        
        # 验证 CORS 头部存在
        assert "access-control-allow-origin" in response.headers


class TestRequestValidation:
    """测试请求验证"""
    
    def test_missing_required_field(self, client):
        """测试缺少必需字段"""
        response = client.post(
            "/api/classify",
            json={}
        )
        
        assert response.status_code == 422
    
    def test_invalid_field_type(self, client):
        """测试无效的字段类型"""
        response = client.post(
            "/api/classify",
            json={"text": 123}  # 应该是字符串
        )
        
        assert response.status_code == 422


@pytest.mark.integration
class TestAPIIntegration:
    """API 集成测试（需要真实的 LLM API）"""
    
    @pytest.mark.asyncio
    async def test_full_translation_flow(self, client, sample_pm_input):
        """测试完整的翻译流程"""
        import os
        if not os.getenv("RUN_INTEGRATION_TESTS"):
            pytest.skip("跳过集成测试（需要设置 RUN_INTEGRATION_TESTS=1）")
        
        # 1. 先分类
        classify_response = client.post(
            "/api/classify",
            json={"text": sample_pm_input}
        )
        
        assert classify_response.status_code == 200
        classify_data = classify_response.json()
        
        # 2. 再翻译
        translate_response = client.post(
            "/api/translate",
            json={"text": sample_pm_input}
        )
        
        assert translate_response.status_code == 200

