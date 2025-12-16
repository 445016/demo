"""
Skill Service
技能读取与提示词组装服务
"""
import logging
from pathlib import Path
from fastapi import HTTPException

from config import settings


# 获取日志器
logger = logging.getLogger(__name__)


def read_skill(skill_name: str, source_role: str = None, target_role: str = None) -> str:
    """
    基于主 Prompt + 模块注入生成完整的 prompt（综合版本）
    
    新架构（V3 - 综合版）：
    - 主 Prompt：prompts/translator.md（包含骨架、约束、Few-shot）
    - 模块注入：
      - modules/roles/{source_role}.md
      - modules/roles/{target_role}.md  
      - modules/rules/format-rules.md
    - 优势：强约束 + 可复用 + 易维护
    
    Args:
        skill_name: skill 文件名（不含 .md），如 "classifier", "translator"
        source_role: 源角色（如 "pm", "dev"），仅用于 translator
        target_role: 目标角色（如 "dev", "pm"），仅用于 translator
        
    Returns:
        完整的Skill提示词
    """
    
    # 对于 classifier
    if skill_name == 'classifier':
        classifier_file = settings.prompts_dir / "classifier.md"
        if classifier_file.exists():
            with open(classifier_file, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Classifier 文件不存在"
            )
    
    # 对于 translator，使用主 Prompt + 模块注入
    if skill_name == 'translator':
        if not source_role or not target_role:
            raise HTTPException(
                status_code=400,
                detail="translator 需要指定 source_role 和 target_role"
            )
        
        logger.debug(f"Loading translator skill: {source_role} -> {target_role}")
        
        # 1. 读取主 Prompt
        main_prompt_file = settings.prompts_dir / "translator.md"
        if not main_prompt_file.exists():
            logger.error(f"Main prompt file not found: {main_prompt_file}")
            raise HTTPException(
                status_code=404,
                detail=f"主 Prompt 文件不存在: translator.md"
            )
        
        with open(main_prompt_file, 'r', encoding='utf-8') as f:
            prompt = f.read()
        
        logger.debug(f"Loaded main prompt: {len(prompt)} chars")
        
        # 2. 读取模块内容
        # 源角色
        source_role_file = settings.modules_dir / "roles" / f"{source_role}.md"
        if not source_role_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"角色文件不存在: {source_role}"
            )
        with open(source_role_file, 'r', encoding='utf-8') as f:
            source_role_content = f.read()
        
        # 目标角色
        target_role_file = settings.modules_dir / "roles" / f"{target_role}.md"
        if not target_role_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"角色文件不存在: {target_role}"
            )
        with open(target_role_file, 'r', encoding='utf-8') as f:
            target_role_content = f.read()
        
        # 格式规则
        rules_file = settings.modules_dir / "rules" / "format-rules.md"
        if not rules_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"规则文件不存在: format-rules.md"
            )
        with open(rules_file, 'r', encoding='utf-8') as f:
            rules_content = f.read()
        
        # 3. 替换变量
        prompt = prompt.replace("{{SOURCE_ROLE}}", source_role.upper())
        prompt = prompt.replace("{{TARGET_ROLE}}", target_role.upper())
        prompt = prompt.replace("{{SOURCE_ROLE_CONTENT}}", source_role_content)
        prompt = prompt.replace("{{TARGET_ROLE_CONTENT}}", target_role_content)
        prompt = prompt.replace("{{FORMAT_RULES}}", rules_content)
        
        return prompt
    
    # 其他 skill（目前不支持）
    raise HTTPException(
        status_code=400,
        detail=f"不支持的 skill: {skill_name}"
    )

