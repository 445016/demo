"""
Communication Translator - Main Application
职能沟通翻译助手后端服务

FastAPI 规范架构：
- config.py: 配置管理
- app/models/: Pydantic 数据模型
- app/services/: 业务逻辑服务
- app/routers/: API 路由
- main.py: 应用入口
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from app.core.logging import setup_logging, get_logger
from app.core.middleware import RequestLoggingMiddleware
from app.routers import api


# ============================================================================
# Logging Configuration
# ============================================================================

# 配置日志（使用 FastAPI/Uvicorn 标准方式）
setup_logging()
logger = get_logger(__name__)


# ============================================================================
# Application Lifecycle
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # Startup
    logger.info("="*80)
    logger.info("Communication Translator - 启动中...")
    logger.info("="*80)
    
    # 验证配置
    if not settings.validate():
        logger.error("配置验证失败，请检查配置")
        raise RuntimeError("配置验证失败")
    
    logger.info(f"✅ LLM Model: {settings.llm_model}")
    logger.info(f"✅ Server: {settings.host}:{settings.port}")
    logger.info(f"✅ AI Context Dir: {settings.ai_context_dir}")
    logger.info("="*80)
    logger.info("🚀 Communication Translator 启动成功")
    logger.info("="*80)
    
    yield
    
    # Shutdown
    logger.info("="*80)
    logger.info("Communication Translator - 正在关闭...")
    logger.info("="*80)


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Communication Translator",
    description="企业职能沟通翻译引擎 - 帮助产品和开发相互理解",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# CORS配置（从 settings 读取）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins_list,
    allow_credentials=settings.allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求日志中间件
app.add_middleware(RequestLoggingMiddleware)


# ============================================================================
# Register Routers
# ============================================================================

app.include_router(api.router)


# ============================================================================
# Static Files & Root Routes
# ============================================================================

# 挂载静态文件
app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """返回前端页面"""
    html_file = settings.static_dir / "index.html"
    
    if not html_file.exists():
        return HTMLResponse(
            content="<h1>Communication Translator</h1><p>前端页面未找到</p>",
            status_code=404
        )
    
    with open(html_file, 'r', encoding='utf-8') as f:
        return HTMLResponse(content=f.read())


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

