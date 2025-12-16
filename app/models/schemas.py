"""
Pydantic Schemas
数据模型定义
"""
from typing import Optional
from pydantic import BaseModel, Field


class ClassifyRequest(BaseModel):
    """分类请求"""
    text: str = Field(..., description="待分类的文本")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "我们需要一个用户登录功能"
            }
        }


class TranslateRequest(BaseModel):
    """翻译请求"""
    text: str = Field(..., description="待翻译的文本")
    source_role: Optional[str] = Field(None, description="源角色，如 pm, dev")
    target_role: Optional[str] = Field(None, description="目标角色，如 dev, pm")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "我们需要实现一个推荐系统",
                "source_role": "pm",
                "target_role": "dev"
            }
        }


class ClassificationResult(BaseModel):
    """分类结果"""
    type: str = Field(..., description="内容类型")
    confidence: float = Field(..., description="置信度", ge=0, le=1)
    reasoning: str = Field(..., description="判断理由")
    keywords: list[str] = Field(default_factory=list, description="关键词列表")
    action: str = Field(..., description="建议的操作")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "产品需求",
                "confidence": 0.95,
                "reasoning": "包含用户需求和功能描述",
                "keywords": ["登录", "功能", "用户"],
                "action": "translate"
            }
        }

