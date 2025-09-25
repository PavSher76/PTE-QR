"""
Enhanced logging configuration for PTE-QR application
"""

import logging
import logging.handlers
import os
import sys
from typing import Any, Dict

import structlog
from structlog.stdlib import LoggerFactory

from app.core.config import settings


def configure_logging() -> None:
    """Configure structured logging with debug support"""
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(settings.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure standard library logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format="%(message)s",
        stream=sys.stdout,
    )
    
    # Configure file handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=settings.LOG_MAX_SIZE,
        backupCount=settings.LOG_BACKUP_COUNT,
    )
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Add file handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    
    # Configure structlog processors
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Add appropriate renderer based on format
    if settings.LOG_FORMAT == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)


class DebugLogger:
    """Enhanced debug logger with context management"""
    
    def __init__(self, name: str = None):
        self.logger = get_logger(name)
        self.context: Dict[str, Any] = {}
    
    def bind(self, **kwargs) -> "DebugLogger":
        """Bind context to logger"""
        self.context.update(kwargs)
        return self
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with context"""
        self.logger.debug(message, **{**self.context, **kwargs})
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message with context"""
        self.logger.info(message, **{**self.context, **kwargs})
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with context"""
        self.logger.warning(message, **{**self.context, **kwargs})
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message with context"""
        self.logger.error(message, **{**self.context, **kwargs})
    
    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback"""
        self.logger.exception(message, **{**self.context, **kwargs})


def log_function_call(func_name: str, **kwargs) -> None:
    """Log function call with parameters"""
    logger = get_logger()
    logger.debug(
        "Function call",
        function=func_name,
        parameters=kwargs,
    )


def log_function_result(func_name: str, result: Any = None, **kwargs) -> None:
    """Log function result"""
    logger = get_logger()
    logger.debug(
        "Function result",
        function=func_name,
        result=result,
        **kwargs,
    )


def log_database_operation(operation: str, table: str, **kwargs) -> None:
    """Log database operation"""
    logger = get_logger()
    logger.debug(
        "Database operation",
        operation=operation,
        table=table,
        **kwargs,
    )


def log_api_request(method: str, endpoint: str, **kwargs) -> None:
    """Log API request details"""
    logger = get_logger()
    logger.debug(
        "API request",
        method=method,
        endpoint=endpoint,
        **kwargs,
    )


def log_api_response(status_code: int, duration: float, **kwargs) -> None:
    """Log API response details"""
    logger = get_logger()
    logger.debug(
        "API response",
        status_code=status_code,
        duration=duration,
        **kwargs,
    )


def log_external_service_call(service: str, endpoint: str, **kwargs) -> None:
    """Log external service call"""
    logger = get_logger()
    logger.debug(
        "External service call",
        service=service,
        endpoint=endpoint,
        **kwargs,
    )


def log_file_operation(operation: str, file_path: str, **kwargs) -> None:
    """Log file operation"""
    logger = get_logger()
    logger.debug(
        "File operation",
        operation=operation,
        file_path=file_path,
        **kwargs,
    )


def log_cache_operation(operation: str, key: str, **kwargs) -> None:
    """Log cache operation"""
    logger = get_logger()
    logger.debug(
        "Cache operation",
        operation=operation,
        key=key,
        **kwargs,
    )
