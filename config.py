"""
Configuration Management
配置管理模块 - 使用 Pydantic Settings（FastAPI 推荐方式）
"""
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    应用配置类
    使用 Pydantic BaseSettings 自动从环境变量读取配置
    """
    
    # ============================================================================
    # LLM 配置（必须通过 .env 文件或环境变量配置）
    # ============================================================================
    
    llm_api_key: str
    llm_base_url: str
    llm_model: str
    
    # ============================================================================
    # 服务器配置
    # ============================================================================
    
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # ============================================================================
    # 日志配置
    # ============================================================================
    
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    log_backup_count: int = 30  # 保留多少天的日志
    
    # ============================================================================
    # CORS 配置
    # ============================================================================
    
    allow_origins: str = "*"  # 逗号分隔的源列表，或使用 "*" 允许所有
    allow_credentials: bool = True
    
    @property
    def allow_origins_list(self) -> List[str]:
        """将 allow_origins 字符串转换为列表"""
        if self.allow_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.allow_origins.split(",")]
    
    # ============================================================================
    # Pydantic Settings 配置
    # ============================================================================
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ============================================================================
    # 路径属性（动态计算）
    # ============================================================================
    
    @property
    def project_root(self) -> Path:
        """项目根目录"""
        return Path(__file__).parent
    
    @property
    def ai_context_dir(self) -> Path:
        """AI Context 目录"""
        return self.project_root / "ai-context"
    
    @property
    def prompts_dir(self) -> Path:
        """Prompts 目录"""
        return self.ai_context_dir / "prompts"
    
    @property
    def modules_dir(self) -> Path:
        """Modules 目录"""
        return self.ai_context_dir / "modules"
    
    @property
    def static_dir(self) -> Path:
        """Static 目录"""
        return self.project_root / "static"
    
    @property
    def logs_dir(self) -> Path:
        """日志目录"""
        return self.project_root / "logs"
    
    @property
    def log_file_path(self) -> Path:
        """完整的日志文件路径"""
        return self.project_root / self.log_file
    
    # ============================================================================
    # 配置验证方法
    # ============================================================================
    
    def validate(self) -> bool:
        """验证配置是否有效"""
        errors = []
        
        # 检查必需的配置
        if not self.llm_api_key:
            errors.append("❌ llm_api_key 未配置")
        
        if not self.llm_base_url:
            errors.append("❌ llm_base_url 未配置")
        
        if not self.llm_model:
            errors.append("❌ llm_model 未配置")
        
        # 检查目录是否存在
        if not self.ai_context_dir.exists():
            errors.append(f"❌ AI Context 目录不存在: {self.ai_context_dir}")
        
        if not self.prompts_dir.exists():
            errors.append(f"❌ Prompts 目录不存在: {self.prompts_dir}")
        
        if errors:
            print("\n".join(errors))
            return False
        
        # 确保日志目录存在
        self.logs_dir.mkdir(exist_ok=True)
        
        return True
    
    def display(self):
        """显示当前配置"""
        print("="*80)
        print("当前配置")
        print("="*80)
        print(f"LLM API Key: {self.llm_api_key[:20]}...")
        print(f"LLM Base URL: {self.llm_base_url}")
        print(f"LLM Model: {self.llm_model}")
        print(f"Host: {self.host}")
        print(f"Port: {self.port}")
        print(f"Debug: {self.debug}")
        print(f"Log Level: {self.log_level}")
        print(f"AI Context Dir: {self.ai_context_dir}")
        print("="*80)


# 全局配置实例（自动从 .env 文件和环境变量读取）
settings = Settings()


if __name__ == "__main__":
    # 测试配置
    settings.display()
    
    if settings.validate():
        print("\n✅ 配置验证通过")
    else:
        print("\n❌ 配置验证失败")

