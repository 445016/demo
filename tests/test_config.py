"""
测试配置管理
"""
import pytest
from pathlib import Path
import os


class TestSettings:
    """测试配置类"""
    
    def test_settings_properties(self):
        """测试配置属性"""
        from config import settings
        
        # 测试路径属性
        assert isinstance(settings.project_root, Path)
        assert isinstance(settings.ai_context_dir, Path)
        assert isinstance(settings.prompts_dir, Path)
        assert isinstance(settings.modules_dir, Path)
        assert isinstance(settings.static_dir, Path)
        assert isinstance(settings.logs_dir, Path)
        
        # 测试路径存在性
        assert settings.project_root.exists()
        assert settings.ai_context_dir.exists()
        assert settings.prompts_dir.exists()
        assert settings.modules_dir.exists()
        assert settings.static_dir.exists()
    
    def test_log_file_path(self):
        """测试日志文件路径"""
        from config import settings
        
        log_path = settings.log_file_path
        assert isinstance(log_path, Path)
        assert str(log_path).endswith("app.log") or "logs" in str(log_path)
    
    def test_allow_origins_list(self):
        """测试 CORS 配置转换"""
        from config import settings
        
        origins = settings.allow_origins_list
        assert isinstance(origins, list)
        assert len(origins) > 0
    
    def test_settings_validation(self):
        """测试配置验证"""
        from config import settings
        
        # 配置验证应该成功（因为在 conftest.py 中设置了测试环境变量）
        is_valid = settings.validate()
        assert is_valid is True


class TestConfigModule:
    """测试配置模块"""
    
    def test_config_import(self):
        """测试配置模块可以正常导入"""
        import config
        assert hasattr(config, 'settings')
        assert hasattr(config, 'Settings')
    
    def test_settings_singleton(self):
        """测试 settings 是单例"""
        from config import settings as settings1
        from config import settings as settings2
        
        assert settings1 is settings2


class TestEnvironmentVariables:
    """测试环境变量处理"""
    
    def test_env_file_loading(self):
        """测试 .env 文件加载"""
        from config import settings
        
        # 在测试环境中，环境变量应该已经被加载
        assert settings.llm_api_key is not None
        assert settings.llm_base_url is not None
        assert settings.llm_model is not None
    
    def test_default_values(self):
        """测试默认值"""
        from config import settings
        
        # 测试有默认值的配置项
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert isinstance(settings.debug, bool)
        assert settings.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert settings.log_backup_count >= 0


class TestConfigPaths:
    """测试配置路径"""
    
    def test_ai_context_structure(self):
        """测试 ai-context 目录结构"""
        from config import settings
        
        # 测试 prompts 目录
        assert settings.prompts_dir.exists()
        assert (settings.prompts_dir / "classifier.md").exists()
        assert (settings.prompts_dir / "translator.md").exists()
        
        # 测试 modules 目录
        assert settings.modules_dir.exists()
        assert (settings.modules_dir / "roles").exists()
        assert (settings.modules_dir / "rules").exists()
        
        # 测试 roles
        roles_dir = settings.modules_dir / "roles"
        assert (roles_dir / "pm.md").exists()
        assert (roles_dir / "dev.md").exists()
        
        # 测试 rules
        rules_dir = settings.modules_dir / "rules"
        assert (rules_dir / "format-rules.md").exists()
    
    def test_static_dir_exists(self):
        """测试 static 目录存在"""
        from config import settings
        
        assert settings.static_dir.exists()
        assert (settings.static_dir / "index.html").exists()

