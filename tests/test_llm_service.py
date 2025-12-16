"""
测试 LLM 服务
注意：这些测试需要 mock LLM API 调用，或者在有 API Key 的情况下运行集成测试
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import json

from app.services.llm_service import classify_input, translate_stream
from app.models.schemas import ClassificationResult


class TestClassifyInput:
    """测试分类功能"""
    
    @pytest.mark.asyncio
    @patch('app.services.llm_service.get_llm_client')
    async def test_classify_product_requirement(self, mock_get_client, sample_pm_input):
        """测试分类产品需求"""
        # Mock LLM 响应
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [Mock(text=json.dumps({
            "type": "产品需求",
            "speaker_view": "pm",
            "confidence": 0.95,
            "reasoning": "包含功能需求和用户视角",
            "keywords": ["用户", "登录", "功能"],
            "action": "translate"
        }))]
        mock_client.messages.create.return_value = mock_message
        mock_get_client.return_value = mock_client
        
        # 执行测试
        result = await classify_input(sample_pm_input)
        
        # 验证结果
        assert isinstance(result, ClassificationResult)
        assert result.type == "产品需求"
        assert result.speaker_view == "pm"
        assert result.confidence >= 0.8
        assert result.action == "translate"
        assert "登录" in result.keywords or "功能" in result.keywords
    
    @pytest.mark.asyncio
    @patch('app.services.llm_service.get_llm_client')
    async def test_classify_technical_solution(self, mock_get_client, sample_dev_input):
        """测试分类技术方案"""
        # Mock LLM 响应
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [Mock(text=json.dumps({
            "type": "技术方案",
            "speaker_view": "dev",
            "confidence": 0.92,
            "reasoning": "包含性能指标和技术实现",
            "keywords": ["数据库", "优化", "Redis", "QPS"],
            "action": "translate"
        }))]
        mock_client.messages.create.return_value = mock_message
        mock_get_client.return_value = mock_client
        
        # 执行测试
        result = await classify_input(sample_dev_input)
        
        # 验证结果
        assert isinstance(result, ClassificationResult)
        assert result.type == "技术方案"
        assert result.speaker_view == "dev"
        assert result.confidence >= 0.8
        assert result.action == "translate"
    
    @pytest.mark.asyncio
    @patch('app.services.llm_service.get_llm_client')
    async def test_classify_insufficient_info(self, mock_get_client, sample_short_input):
        """测试分类信息不足的输入"""
        # Mock LLM 响应
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [Mock(text=json.dumps({
            "type": "不明确",
            "speaker_view": "unknown",
            "confidence": 0.45,
            "reasoning": "输入过短，信息不足",
            "keywords": ["功能"],
            "action": "clarify"
        }))]
        mock_client.messages.create.return_value = mock_message
        mock_get_client.return_value = mock_client
        
        # 执行测试
        result = await classify_input(sample_short_input)
        
        # 验证结果
        assert isinstance(result, ClassificationResult)
        assert result.type == "不明确"
        assert result.confidence < 0.7
        assert result.action == "clarify"


class TestTranslateStream:
    """测试翻译流式输出"""
    
    @pytest.mark.asyncio
    @patch('app.services.llm_service.get_llm_client')
    async def test_translate_stream_basic(self, mock_get_client, sample_pm_input):
        """测试基本的翻译流式输出"""
        # Mock LLM 流式响应
        mock_client = Mock()
        mock_stream = Mock()
        
        # 模拟流式输出
        mock_stream.text_stream = iter([
            "[理解确认]\n\n",
            "我理解您的需求...\n\n",
            "[需求技术化描述]\n\n",
            "从技术角度..."
        ])
        
        mock_final_message = Mock()
        mock_final_message.usage.input_tokens = 1000
        mock_final_message.usage.output_tokens = 500
        mock_stream.get_final_message.return_value = mock_final_message
        
        mock_stream.__enter__ = Mock(return_value=mock_stream)
        mock_stream.__exit__ = Mock(return_value=False)
        
        mock_client.messages.stream.return_value = mock_stream
        mock_get_client.return_value = mock_client
        
        # 执行测试
        chunks = []
        async for chunk in translate_stream(sample_pm_input, "pm", "dev"):
            chunks.append(chunk)
        
        # 验证结果
        assert len(chunks) > 0
        full_output = ''.join(chunks)
        assert "理解确认" in full_output
    
    @pytest.mark.asyncio
    @patch('app.services.llm_service.get_llm_client')
    async def test_translate_with_mode_and_classification(self, mock_get_client, sample_pm_input):
        """测试带模式和分类信息的翻译"""
        # Mock LLM 流式响应
        mock_client = Mock()
        mock_stream = Mock()
        mock_stream.text_stream = iter(["[理解确认]\n\n", "测试内容"])
        mock_final_message = Mock()
        mock_final_message.usage.input_tokens = 1000
        mock_final_message.usage.output_tokens = 500
        mock_stream.get_final_message.return_value = mock_final_message
        mock_stream.__enter__ = Mock(return_value=mock_stream)
        mock_stream.__exit__ = Mock(return_value=False)
        mock_client.messages.stream.return_value = mock_stream
        mock_get_client.return_value = mock_client
        
        # 执行测试（带模式和分类信息）
        chunks = []
        async for chunk in translate_stream(
            sample_pm_input, 
            "pm", 
            "dev",
            mode="auto",
            classification_type="产品需求",
            classification_confidence=0.95
        ):
            chunks.append(chunk)
        
        # 验证结果
        assert len(chunks) > 0


@pytest.mark.integration
class TestLLMServiceIntegration:
    """集成测试（需要真实的 API Key）
    
    运行方式：
    pytest -m integration tests/test_llm_service.py
    """
    
    @pytest.mark.asyncio
    async def test_real_classify(self, sample_pm_input):
        """真实的分类测试（需要 API Key）"""
        # 这个测试需要真实的 LLM API
        # 只在有环境变量时运行
        import os
        if not os.getenv("RUN_INTEGRATION_TESTS"):
            pytest.skip("跳过集成测试（需要设置 RUN_INTEGRATION_TESTS=1）")
        
        result = await classify_input(sample_pm_input)
        
        assert isinstance(result, ClassificationResult)
        assert result.type in ["产品需求", "技术方案", "不明确"]
        assert 0 <= result.confidence <= 1
        assert result.action in ["translate", "clarify", "split", "reject"]
    
    @pytest.mark.asyncio
    async def test_real_translate(self, sample_pm_input):
        """真实的翻译测试（需要 API Key）"""
        import os
        if not os.getenv("RUN_INTEGRATION_TESTS"):
            pytest.skip("跳过集成测试（需要设置 RUN_INTEGRATION_TESTS=1）")
        
        chunks = []
        async for chunk in translate_stream(sample_pm_input, "pm", "dev"):
            chunks.append(chunk)
        
        full_output = ''.join(chunks)
        
        # 验证输出包含预期的 Section
        assert "[理解确认]" in full_output or "理解确认" in full_output
        assert len(full_output) > 100  # 输出应该有一定长度

