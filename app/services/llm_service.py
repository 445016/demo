"""
LLM Service
LLM 交互服务
"""
import json
import logging
from typing import AsyncIterator
from datetime import datetime

from anthropic import Anthropic, APIError
from fastapi import HTTPException

from config import settings
from app.models.schemas import ClassificationResult
from app.services.skill_service import read_skill


# 获取日志器（FastAPI 标准方式）
logger = logging.getLogger(__name__)


def get_llm_client() -> Anthropic:
    """获取 LLM 客户端（智谱 GLM-4.6，使用 Anthropic API 格式）"""
    return Anthropic(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key
    )


async def classify_input(text: str) -> ClassificationResult:
    """
    分类用户输入
    
    Args:
        text: 用户输入内容
        
    Returns:
        分类结果
    """
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    
    logger.info(f"[CLASSIFY REQUEST] ID: {request_id}, Input: {text[:50]}...")
    
    # 读取分类器 Skill
    classifier_prompt = read_skill("classifier")
    
    # 调用 LLM
    client = get_llm_client()
    
    try:
        message = client.messages.create(
            model=settings.llm_model,
            max_tokens=1000,
            system=classifier_prompt,
            messages=[
                {"role": "user", "content": text}
            ]
        )
        
        # 解析 JSON 结果
        result_text = message.content[0].text
        
        # 尝试提取 JSON（可能包含在 ```json 代码块中）
        if "```json" in result_text:
            json_start = result_text.find("```json") + 7
            json_end = result_text.find("```", json_start)
            result_text = result_text[json_start:json_end].strip()
        elif "```" in result_text:
            json_start = result_text.find("```") + 3
            json_end = result_text.find("```", json_start)
            result_text = result_text[json_start:json_end].strip()
        
        result_json = json.loads(result_text)
        
        logger.info(f"[CLASSIFY SUCCESS] Type: {result_json.get('type')}, Confidence: {result_json.get('confidence')}, "
                   f"Tokens: {message.usage.input_tokens}/{message.usage.output_tokens}")
        
        return ClassificationResult(**result_json)
        
    except json.JSONDecodeError as e:
        logger.error(f"[CLASSIFY ERROR] JSON Parse Failed: {str(e)}, Response: {result_text[:200]}")
        raise HTTPException(
            status_code=500,
            detail=f"分类结果JSON解析失败: {str(e)}\n原始响应: {result_text[:200]}"
        )
    except APIError as e:
        logger.error(f"[CLASSIFY ERROR] API Error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"LLM API 调用失败: {str(e)}"
        )


def format_output_chunk(chunk: str) -> str:
    """
    不做任何处理，直接返回LLM原始输出
    让前端来处理转义字符，避免破坏SSE格式
    
    Args:
        chunk: 当前文本片段
        
    Returns:
        原始chunk
    """
    # 不做任何处理！保持LLM原始输出
    # 前端会处理 \\n -> \n 的转换
    return chunk


async def translate_stream(
    text: str, 
    source_role: str, 
    target_role: str,
    mode: str = "manual",
    classification_type: str = None,
    classification_confidence: float = None
) -> AsyncIterator[str]:
    """
    流式翻译
    
    Args:
        text: 用户输入
        source_role: 源角色（如 "pm", "dev"）
        target_role: 目标角色（如 "dev", "pm"）
        mode: 翻译模式（"auto" 或 "manual"）
        classification_type: 分类类型（如果是自动识别）
        classification_confidence: 分类置信度（如果是自动识别）
        
    Yields:
        翻译结果的文本片段
    """
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    
    logger.info(f"[TRANSLATE REQUEST] ID: {request_id}, {source_role.upper()} → {target_role.upper()}, Input: {text[:50]}...")
    
    # 读取翻译 Skill（translator + roles）
    translator_prompt = read_skill("translator", source_role, target_role)
    
    # 调用 LLM 流式生成
    client = get_llm_client()
    
    chunk_count = 0
    total_length = 0
    full_output = []  # 记录完整输出
    
    try:
        with client.messages.stream(
            model=settings.llm_model,
            max_tokens=4000,
            system=translator_prompt,
            messages=[
                {"role": "user", "content": text}
            ]
        ) as stream:
            for text_chunk in stream.text_stream:
                chunk_count += 1
                total_length += len(text_chunk)
                
                # 格式化输出
                formatted = format_output_chunk(text_chunk)
                
                # 保存到完整输出
                full_output.append(formatted)
                
                yield formatted
            
            # 记录完整输出到单独的文件
            complete_output = ''.join(full_output)
            output_file = settings.logs_dir / f"llm_output_{request_id}.txt"
            
            # 构建分类信息（如果是自动识别）
            classification_info = ""
            if mode == 'auto' and classification_type:
                classification_info = f"Classification Type: {classification_type}"
                if classification_confidence is not None:
                    classification_info += f" (置信度: {classification_confidence:.0%})"
                classification_info += "\n"
            
            # 使用 logging 写入（创建独立的 FileHandler）
            llm_file_logger = logging.getLogger(f"llm_output_{request_id}")
            llm_file_logger.setLevel(logging.INFO)
            llm_file_logger.propagate = False  # 不传播到父 logger
            
            # 创建文件处理器（无格式化，直接写入原始内容）
            file_handler = logging.FileHandler(output_file, mode='w', encoding='utf-8')
            file_handler.setFormatter(logging.Formatter('%(message)s'))  # 只输出消息本身
            llm_file_logger.addHandler(file_handler)
            
            # 写入日志内容
            llm_file_logger.info('=' * 80)
            llm_file_logger.info(f"Request ID: {request_id}")
            llm_file_logger.info(f"Mode: {'自动识别' if mode == 'auto' else '手动选择'}")
            if classification_info:
                llm_file_logger.info(classification_info.rstrip('\n'))
            llm_file_logger.info(f"Translation: {source_role.upper()} → {target_role.upper()}")
            llm_file_logger.info(f"User Input: {text}")
            llm_file_logger.info('=' * 80)
            llm_file_logger.info("")
            llm_file_logger.info("【System Prompt】")
            llm_file_logger.info("")
            llm_file_logger.info(translator_prompt)
            llm_file_logger.info("")
            llm_file_logger.info('=' * 80)
            llm_file_logger.info("")
            llm_file_logger.info("【LLM 完整输出】")
            llm_file_logger.info("")
            llm_file_logger.info(complete_output)
            llm_file_logger.info("")
            llm_file_logger.info('=' * 80)
            llm_file_logger.info("【输出统计】")
            llm_file_logger.info(f"总 Chunk 数: {chunk_count}")
            llm_file_logger.info(f"总字符数: {total_length}")
            llm_file_logger.info(f"换行符数量: {complete_output.count(chr(10))}")
            llm_file_logger.info('=' * 80)
            
            # 清理 handler，避免内存泄漏
            file_handler.close()
            llm_file_logger.removeHandler(file_handler)
            
            # 记录最终使用情况
            final_message = stream.get_final_message()
            if final_message:
                logger.info(f"[TRANSLATE SUCCESS] Chunks: {chunk_count}, Chars: {total_length}, "
                           f"Tokens: {final_message.usage.input_tokens}/{final_message.usage.output_tokens}, "
                           f"Output: {output_file.name}")
                
    except APIError as e:
        logger.error(f"[TRANSLATE ERROR] {str(e)}")
        yield f"\n\n[错误] LLM API 调用失败: {str(e)}"

