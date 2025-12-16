"""
API Routes
API 路由定义
"""
import asyncio
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse

from app.models.schemas import ClassifyRequest, TranslateRequest, ClassificationResult
from app.services.llm_service import classify_input, translate_stream


# 获取日志器
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])


@router.post("/classify", response_model=ClassificationResult)
async def classify(request: ClassifyRequest) -> ClassificationResult:
    """
    分类用户输入
    
    Args:
        request: 分类请求
        
    Returns:
        JSON 格式的分类结果
    """
    if not request.text or len(request.text.strip()) < 5:
        raise HTTPException(
            status_code=400,
            detail="输入内容过短，至少需要5个字符"
        )
    
    result = await classify_input(request.text)
    return result


@router.post("/translate")
async def translate(request: TranslateRequest):
    """
    翻译（自动分类或手动指定角色）
    
    Args:
        request: 翻译请求
        
    Returns:
        SSE 流式响应
    """
    if not request.text or len(request.text.strip()) < 5:
        raise HTTPException(
            status_code=400,
            detail="输入内容过短，至少需要5个字符"
        )
    
    # 记录用户选择的模式
    if not request.source_role or not request.target_role:
        mode_info = "自动识别"
        logger.info(f"[翻译模式] {mode_info} | 输入: {request.text[:50]}...")
    else:
        mode_info = f"{request.source_role.upper()} → {request.target_role.upper()}"
        logger.info(f"[翻译模式] {mode_info} | 输入: {request.text[:50]}...")
    
    # 如果没有指定角色，先分类
    if not request.source_role or not request.target_role:
        classification = await classify_input(request.text)
        
        # 根据 action 决定下一步
        if classification.action == "clarify":
            # 需要澄清
            logger.info(f"[自动识别结果] 需要澄清 | 原因: {classification.reasoning}")
            async def clarify_response():
                yield "data: [输入信息不足]\n\n"
                yield "data: \n\n"
                yield "data: 为了更好地帮助您，请补充：\n\n"
                yield "data: 1. 如果这是产品需求，请说明：想解决什么问题？预期目标？\n\n"
                yield "data: 2. 如果这是技术方案，请说明：改动背景？解决什么问题？\n\n"
                yield "data: [END]\n\n"
            
            return StreamingResponse(
                clarify_response(),
                media_type="text/event-stream"
            )
        
        elif classification.action == "split":
            # 需要拆分话题
            logger.info(f"[自动识别结果] 需要拆分话题 | 原因: {classification.reasoning}")
            async def split_response():
                yield "data: [检测到多个话题]\n\n"
                yield "data: \n\n"
                yield f"data: 建议分别讨论以下话题：\n\n"
                yield "data: 请选择其中一个话题重新输入。\n\n"
                yield "data: [END]\n\n"
            
            return StreamingResponse(
                split_response(),
                media_type="text/event-stream"
            )
        
        # 根据分类类型映射到角色组合
        role_map = {
            "产品需求": ("pm", "dev"),           # 产品需求 → 翻译给开发
            "技术方案": ("dev", "pm"),           # 技术方案 → 翻译给产品
            "运营数据": ("operation", "dev"),   # 运营数据需求 → 翻译给开发
            "管理决策": ("management", "pm")    # 管理决策 → 翻译给产品经理
        }
        
        role_pair = role_map.get(classification.type)
        
        if not role_pair:
            raise HTTPException(
                status_code=400,
                detail=f"未知的分类类型: {classification.type}"
            )
        
        source_role, target_role = role_pair
        logger.info(f"[自动识别结果] 分类: {classification.type} (置信度: {classification.confidence:.0%}) → {source_role.upper()} → {target_role.upper()}")
        
        # 保存分类信息用于后续传递
        mode = "auto"
        classification_type = classification.type
        classification_confidence = classification.confidence
    else:
        source_role = request.source_role
        target_role = request.target_role
        classification = None  # 手动指定角色时不需要分类结果
        mode = "manual"
        classification_type = None
        classification_confidence = None
    
    # 流式翻译
    async def generate():
        try:
            # 发送初始连接确认（强制开始流式传输）
            yield ": connected\n\n"
            
            # 先发送分类信息（如果是自动分类的）
            if classification:
                # 发送分类结果，后面加两个空行分隔
                yield f"data: [分类结果: {classification.type} (置信度: {classification.confidence:.0%})]\n"
                yield "data: \n"
                yield "\n"
                await asyncio.sleep(0)  # 让出控制权，立即发送
            
            # 发送翻译结果
            async for chunk in translate_stream(
                request.text, 
                source_role, 
                target_role,
                mode=mode,
                classification_type=classification_type,
                classification_confidence=classification_confidence
            ):
                # SSE规范：如果chunk包含换行符，必须拆分成多个data:行
                # 前端会自动用\n连接连续的data:行
                for line in chunk.split('\n'):
                    yield f"data: {line}\n"
                yield "\n"  # 消息结束
                await asyncio.sleep(0)  # 立即发送，不缓冲
                
            # 结束标记
            yield "data: [END]\n\n"
            
        except Exception as e:
            yield f"data: \n\n[错误] {str(e)}\n\n"
            yield "data: [END]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/health")
async def health():
    """
    健康检查
    
    Returns:
        服务状态
    """
    return {
        "status": "healthy",
        "service": "Communication Translator"
    }

