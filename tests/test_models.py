"""
测试 Pydantic 数据模型
"""
import pytest
from pydantic import ValidationError

from app.models.schemas import ClassifyRequest, TranslateRequest, ClassificationResult


class TestClassifyRequest:
    """测试分类请求模型"""
    
    def test_valid_request(self):
        """测试有效的分类请求"""
        request = ClassifyRequest(text="我们需要一个用户登录功能")
        
        assert request.text == "我们需要一个用户登录功能"
    
    def test_empty_text_validation(self):
        """测试空文本验证"""
        with pytest.raises(ValidationError):
            ClassifyRequest(text="")
    
    def test_missing_field(self):
        """测试缺少必需字段"""
        with pytest.raises(ValidationError):
            ClassifyRequest()


class TestTranslateRequest:
    """测试翻译请求模型"""
    
    def test_valid_request_with_roles(self):
        """测试带角色的有效请求"""
        request = TranslateRequest(
            text="我们需要一个用户登录功能",
            source_role="pm",
            target_role="dev"
        )
        
        assert request.text == "我们需要一个用户登录功能"
        assert request.source_role == "pm"
        assert request.target_role == "dev"
    
    def test_valid_request_without_roles(self):
        """测试不带角色的有效请求（自动识别）"""
        request = TranslateRequest(text="我们需要一个用户登录功能")
        
        assert request.text == "我们需要一个用户登录功能"
        assert request.source_role is None
        assert request.target_role is None
    
    def test_partial_roles(self):
        """测试只指定一个角色"""
        # 只指定 source_role
        request1 = TranslateRequest(
            text="测试",
            source_role="pm"
        )
        assert request1.source_role == "pm"
        assert request1.target_role is None
        
        # 只指定 target_role
        request2 = TranslateRequest(
            text="测试",
            target_role="dev"
        )
        assert request2.source_role is None
        assert request2.target_role == "dev"
    
    def test_empty_text_validation(self):
        """测试空文本验证"""
        with pytest.raises(ValidationError):
            TranslateRequest(text="")


class TestClassificationResult:
    """测试分类结果模型"""
    
    def test_valid_result(self):
        """测试有效的分类结果"""
        result = ClassificationResult(
            type="产品需求",
            confidence=0.95,
            reasoning="包含功能需求和用户视角",
            keywords=["用户", "登录", "功能"],
            action="translate"
        )
        
        assert result.type == "产品需求"
        assert result.confidence == 0.95
        assert result.reasoning == "包含功能需求和用户视角"
        assert result.keywords == ["用户", "登录", "功能"]
        assert result.action == "translate"
    
    def test_confidence_range_validation(self):
        """测试置信度范围验证"""
        # 有效的置信度
        result = ClassificationResult(
            type="产品需求",
            confidence=0.5,
            reasoning="测试",
            keywords=[],
            action="translate"
        )
        assert result.confidence == 0.5
        
        # 置信度 < 0（应该失败）
        with pytest.raises(ValidationError):
            ClassificationResult(
                type="产品需求",
                confidence=-0.1,
                reasoning="测试",
                keywords=[],
                action="translate"
            )
        
        # 置信度 > 1（应该失败）
        with pytest.raises(ValidationError):
            ClassificationResult(
                type="产品需求",
                confidence=1.1,
                reasoning="测试",
                keywords=[],
                action="translate"
            )
    
    def test_missing_required_fields(self):
        """测试缺少必需字段"""
        with pytest.raises(ValidationError):
            ClassificationResult(
                type="产品需求",
                confidence=0.95
                # 缺少 reasoning, keywords, action
            )
    
    def test_default_keywords(self):
        """测试 keywords 默认值"""
        result = ClassificationResult(
            type="产品需求",
            confidence=0.95,
            reasoning="测试",
            action="translate"
            # 没有提供 keywords
        )
        
        assert result.keywords == []
    
    def test_json_serialization(self):
        """测试 JSON 序列化"""
        result = ClassificationResult(
            type="产品需求",
            confidence=0.95,
            reasoning="包含功能需求",
            keywords=["用户", "登录"],
            action="translate"
        )
        
        json_data = result.model_dump()
        
        assert json_data["type"] == "产品需求"
        assert json_data["confidence"] == 0.95
        assert json_data["reasoning"] == "包含功能需求"
        assert json_data["keywords"] == ["用户", "登录"]
        assert json_data["action"] == "translate"
    
    def test_json_deserialization(self):
        """测试 JSON 反序列化"""
        json_data = {
            "type": "技术方案",
            "confidence": 0.92,
            "reasoning": "包含技术指标",
            "keywords": ["优化", "性能"],
            "action": "translate"
        }
        
        result = ClassificationResult(**json_data)
        
        assert result.type == "技术方案"
        assert result.confidence == 0.92
        assert result.reasoning == "包含技术指标"
        assert result.keywords == ["优化", "性能"]
        assert result.action == "translate"


class TestModelInteraction:
    """测试模型之间的交互"""
    
    def test_request_response_flow(self):
        """测试请求-响应流程"""
        # 1. 创建分类请求
        classify_request = ClassifyRequest(text="我们需要一个用户登录功能")
        
        # 2. 模拟分类结果
        classification_result = ClassificationResult(
            type="产品需求",
            confidence=0.95,
            reasoning="包含功能需求",
            keywords=["登录", "功能"],
            action="translate"
        )
        
        # 3. 基于分类结果创建翻译请求
        translate_request = TranslateRequest(
            text=classify_request.text,
            source_role="pm",
            target_role="dev"
        )
        
        assert translate_request.text == classify_request.text
        assert translate_request.source_role == "pm"
        assert translate_request.target_role == "dev"

