"""
Middleware
中间件
"""
import time
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件
    记录所有 API 请求的详细信息
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        处理请求
        
        Args:
            request: 请求对象
            call_next: 下一个处理器
            
        Returns:
            响应对象
        """
        # 开始时间
        start_time = time.time()
        
        # 记录请求信息
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"| Client: {request.client.host if request.client else 'Unknown'}"
        )
        
        # 处理请求
        try:
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"| Status: {response.status_code} "
                f"| Time: {process_time:.3f}s"
            )
            
            # 添加处理时间到响应头
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # 记录错误
            process_time = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} "
                f"| Exception: {type(e).__name__}: {str(e)} "
                f"| Time: {process_time:.3f}s"
            )
            raise

