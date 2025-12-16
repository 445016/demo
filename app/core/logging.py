"""
Logging Configuration
日志配置模块 - 使用 FastAPI/Uvicorn 标准日志 + 日志轮转
"""
import logging
import sys
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler

from config import settings


# 标记是否已初始化，防止重复配置
_logging_configured = False


def setup_logging():
    """
    配置应用日志
    使用 Python 标准 logging + Uvicorn 集成 + 按日期轮转
    """
    global _logging_configured
    
    # 如果已经配置过，直接返回（防止重复添加 handler）
    if _logging_configured:
        return logging.getLogger(__name__)
    
    # 确保日志目录存在
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    
    # 日志格式
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # 创建日志格式器
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # 获取根日志器并清理已有的 handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.log_level))
    console_handler.setFormatter(formatter)
    
    # 文件处理器（按日期轮转）
    # when='midnight': 每天午夜轮转
    # interval=1: 每1天
    # backupCount: 保留多少天的日志（从配置读取）
    file_handler = TimedRotatingFileHandler(
        filename=settings.log_file_path,
        when='midnight',
        interval=1,
        backupCount=settings.log_backup_count,
        encoding='utf-8',
        delay=False,
        utc=False
    )
    file_handler.setLevel(getattr(logging, settings.log_level))
    file_handler.setFormatter(formatter)
    # 设置日志文件名后缀格式（YYYYMMDD）
    file_handler.suffix = "%Y%m%d"
    
    # 配置根日志器
    root_logger.setLevel(getattr(logging, settings.log_level))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # 标记已初始化
    _logging_configured = True
    
    # 设置第三方库的日志级别（避免太多噪音）
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.INFO)
    
    return logging.getLogger(__name__)


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志器
    
    Args:
        name: 日志器名称，通常使用 __name__
        
    Returns:
        Logger 实例
    """
    return logging.getLogger(name)

