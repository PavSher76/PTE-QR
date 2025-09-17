"""
FastAPI middleware for metrics and logging
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from app.core.metrics import metrics_collector

logger = structlog.get_logger()


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting HTTP request metrics"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())

        # Add request ID to request state
        request.state.request_id = request_id

        # Start timing
        start_time = time.time()

        # Extract request info
        method = request.method
        endpoint = request.url.path

        # Skip metrics for health checks and metrics endpoints
        if endpoint in ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Record metrics
            metrics_collector.record_request(
                method=method,
                endpoint=endpoint,
                status_code=response.status_code,
                duration=duration,
            )

            # Log request
            logger.info(
                "HTTP request completed",
                request_id=request_id,
                method=method,
                endpoint=endpoint,
                status_code=response.status_code,
                duration=duration,
                user_agent=request.headers.get("user-agent", ""),
                client_ip=request.client.host if request.client else None,
            )

            return response

        except Exception as e:
            # Calculate duration for failed requests
            duration = time.time() - start_time

            # Record metrics for failed request
            metrics_collector.record_request(
                method=method, endpoint=endpoint, status_code=500, duration=duration
            )

            # Log error
            logger.error(
                "HTTP request failed",
                request_id=request_id,
                method=method,
                endpoint=endpoint,
                error=str(e),
                duration=duration,
                user_agent=request.headers.get("user-agent", ""),
                client_ip=request.client.host if request.client else None,
                exc_info=True,
            )

            raise


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured logging"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get request ID from state (set by MetricsMiddleware)
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

        # Create structured logger with request context
        request_logger = logger.bind(
            request_id=request_id,
            method=request.method,
            endpoint=request.url.path,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent", ""),
        )

        # Log request start
        request_logger.info("HTTP request started")

        try:
            response = await call_next(request)

            # Log successful completion
            request_logger.info(
                "HTTP request completed", status_code=response.status_code
            )

            return response

        except Exception as e:
            # Log error
            request_logger.error("HTTP request failed", error=str(e), exc_info=True)
            raise


class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for adding security headers"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        # Add request ID to response headers
        if hasattr(request.state, "request_id"):
            response.headers["X-Request-ID"] = request.state.request_id

        return response


class CORSMiddleware(BaseHTTPMiddleware):
    """CORS middleware for handling cross-origin requests"""

    def __init__(self, app, allow_origins=None, allow_methods=None, allow_headers=None):
        super().__init__(app)
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or [
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "OPTIONS",
        ]
        self.allow_headers = allow_headers or ["*"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
        else:
            response = await call_next(request)

        # Add CORS headers
        origin = request.headers.get("origin")
        if origin in self.allow_origins or "*" in self.allow_origins:
            response.headers["Access-Control-Allow-Origin"] = origin or "*"

        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "86400"

        return response
