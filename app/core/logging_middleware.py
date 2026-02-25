import time
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logger import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()

        response = await call_next(request)

        duration = round((time.time() - start) * 1000, 2)

        logger.info(
            "request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration,
            },
        )

        return response