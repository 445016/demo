"""
测试 Prompt 组装服务
"""
import pytest
from pathlib import Path

from app.services.skill_service import read_skill
from config import settings


class TestSkillService:
    """测试 Prompt 组装服务"""
    
    def test_read_classifier_skill(self):
        """测试读取分类器 Prompt"""
        prompt = read_skill("classifier")
        
        assert prompt is not None
        assert len(prompt) > 0
        assert "分类维度" in prompt
        assert "type" in prompt
        assert "speaker_view" in prompt
        assert "输出格式" in prompt
    
    def test_read_translator_skill_pm_to_dev(self):
        """测试读取翻译器 Prompt（PM → DEV）"""
        prompt = read_skill("translator", "pm", "dev")
        
        assert prompt is not None
        assert len(prompt) > 0
        
        # 检查占位符已被替换
        assert "{{SOURCE_ROLE}}" not in prompt
        assert "{{TARGET_ROLE}}" not in prompt
        assert "{{SOURCE_ROLE_CONTENT}}" not in prompt
        assert "{{TARGET_ROLE_CONTENT}}" not in prompt
        assert "{{FORMAT_RULES}}" not in prompt
        
        # 检查角色已注入
        assert "PM → DEV" in prompt or "pm → dev" in prompt.lower()
        
        # 检查核心内容存在
        assert "理解确认" in prompt
        assert "需求技术化描述" in prompt
        assert "实现方向建议" in prompt
    
    def test_read_translator_skill_dev_to_pm(self):
        """测试读取翻译器 Prompt（DEV → PM）"""
        prompt = read_skill("translator", "dev", "pm")
        
        assert prompt is not None
        assert len(prompt) > 0
        
        # 检查占位符已被替换
        assert "{{SOURCE_ROLE}}" not in prompt
        assert "{{TARGET_ROLE}}" not in prompt
        
        # 检查角色已注入
        assert "DEV → PM" in prompt or "dev → pm" in prompt.lower()
        
        # 检查核心内容存在
        assert "理解确认" in prompt
        assert "对用户体验的影响" in prompt
        assert "对业务指标的影响" in prompt
    
    def test_invalid_skill_name(self):
        """测试无效的 Skill 名称"""
        with pytest.raises(Exception):
            read_skill("invalid_skill")
    
    def test_prompt_files_exist(self):
        """测试 Prompt 文件存在性"""
        assert settings.prompts_dir.exists()
        assert (settings.prompts_dir / "classifier.md").exists()
        assert (settings.prompts_dir / "translator.md").exists()
    
    def test_module_files_exist(self):
        """测试模块文件存在性"""
        assert settings.modules_dir.exists()
        assert (settings.modules_dir / "roles" / "pm.md").exists()
        assert (settings.modules_dir / "roles" / "dev.md").exists()
        assert (settings.modules_dir / "rules" / "format-rules.md").exists()
    
    def test_prompt_content_quality(self):
        """测试 Prompt 内容质量"""
        prompt = read_skill("translator", "pm", "dev")
        
        # 检查是否包含 Few-shot 示例
        assert "示例" in prompt or "Example" in prompt
        
        # 检查是否包含强约束
        assert "必须" in prompt or "禁止" in prompt
        
        # 检查是否包含降级策略
        assert "信息不足" in prompt
        
        # 检查长度合理（应该是完整的 Prompt）
        assert len(prompt) > 1000  # 至少 1000 字符

