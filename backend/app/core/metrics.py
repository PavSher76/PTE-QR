"""
Prometheus metrics collection
"""

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Info,
    CollectorRegistry,
    generate_latest,
)
import time
from typing import Dict, Any
import structlog

logger = structlog.get_logger()

# Create custom registry
registry = CollectorRegistry()

# Request metrics
REQUEST_COUNT = Counter(
    "pte_qr_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"],
    registry=registry,
)

REQUEST_DURATION = Histogram(
    "pte_qr_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    registry=registry,
)

# QR Code metrics
QR_CODES_GENERATED = Counter(
    "pte_qr_codes_generated_total",
    "Total number of QR codes generated",
    ["doc_uid", "revision"],
    registry=registry,
)

QR_CODES_SCANNED = Counter(
    "pte_qr_codes_scanned_total",
    "Total number of QR codes scanned",
    ["doc_uid", "revision", "status"],
    registry=registry,
)

# Document status metrics
DOCUMENT_STATUS_CHECKS = Counter(
    "pte_qr_document_status_checks_total",
    "Total number of document status checks",
    ["doc_uid", "revision", "status"],
    registry=registry,
)

# ENOVIA integration metrics
ENOVIA_REQUESTS = Counter(
    "pte_qr_enovia_requests_total",
    "Total number of ENOVIA API requests",
    ["endpoint", "status"],
    registry=registry,
)

ENOVIA_REQUEST_DURATION = Histogram(
    "pte_qr_enovia_request_duration_seconds",
    "ENOVIA API request duration in seconds",
    ["endpoint"],
    registry=registry,
)

# Cache metrics
CACHE_HITS = Counter(
    "pte_qr_cache_hits_total",
    "Total number of cache hits",
    ["cache_type"],
    registry=registry,
)

CACHE_MISSES = Counter(
    "pte_qr_cache_misses_total",
    "Total number of cache misses",
    ["cache_type"],
    registry=registry,
)

# System metrics
ACTIVE_CONNECTIONS = Gauge(
    "pte_qr_active_connections", "Number of active connections", registry=registry
)

DATABASE_CONNECTIONS = Gauge(
    "pte_qr_database_connections", "Number of database connections", registry=registry
)

REDIS_CONNECTIONS = Gauge(
    "pte_qr_redis_connections", "Number of Redis connections", registry=registry
)

# PDF processing metrics
PDF_STAMPING_OPERATIONS = Counter(
    "pte_qr_pdf_stamping_operations_total",
    "Total number of PDF stamping operations",
    ["operation_type", "status"],
    registry=registry,
)

PDF_PROCESSING_DURATION = Histogram(
    "pte_qr_pdf_processing_duration_seconds",
    "PDF processing duration in seconds",
    ["operation_type"],
    registry=registry,
)

# Authentication metrics
AUTH_ATTEMPTS = Counter(
    "pte_qr_auth_attempts_total",
    "Total number of authentication attempts",
    ["method", "status"],
    registry=registry,
)

AUTH_SUCCESS = Counter(
    "pte_qr_auth_success_total",
    "Total number of successful authentications",
    ["method"],
    registry=registry,
)

# Application info
APP_INFO = Info("pte_qr_app_info", "Application information", registry=registry)

# Set application info
APP_INFO.info(
    {
        "version": "1.0.0",
        "name": "PTE-QR System",
        "description": "Document actuality verification system",
    }
)


class MetricsCollector:
    """Metrics collection and management"""

    def __init__(self):
        self.registry = registry

    def record_request(
        self, method: str, endpoint: str, status_code: int, duration: float
    ):
        """Record HTTP request metrics"""
        REQUEST_COUNT.labels(
            method=method, endpoint=endpoint, status_code=str(status_code)
        ).inc()

        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

    def record_qr_generation(self, doc_uid: str, revision: str):
        """Record QR code generation"""
        QR_CODES_GENERATED.labels(doc_uid=doc_uid, revision=revision).inc()

    def record_qr_scan(self, doc_uid: str, revision: str, status: str):
        """Record QR code scan"""
        QR_CODES_SCANNED.labels(doc_uid=doc_uid, revision=revision, status=status).inc()

    def record_document_status_check(self, doc_uid: str, revision: str, status: str):
        """Record document status check"""
        DOCUMENT_STATUS_CHECKS.labels(
            doc_uid=doc_uid, revision=revision, status=status
        ).inc()

    def record_enovia_request(self, endpoint: str, status: str, duration: float):
        """Record ENOVIA API request"""
        ENOVIA_REQUESTS.labels(endpoint=endpoint, status=status).inc()

        ENOVIA_REQUEST_DURATION.labels(endpoint=endpoint).observe(duration)

    def record_cache_hit(self, cache_type: str):
        """Record cache hit"""
        CACHE_HITS.labels(cache_type=cache_type).inc()

    def record_cache_miss(self, cache_type: str):
        """Record cache miss"""
        CACHE_MISSES.labels(cache_type=cache_type).inc()

    def record_pdf_operation(self, operation_type: str, status: str, duration: float):
        """Record PDF processing operation"""
        PDF_STAMPING_OPERATIONS.labels(
            operation_type=operation_type, status=status
        ).inc()

        PDF_PROCESSING_DURATION.labels(operation_type=operation_type).observe(duration)

    def record_auth_attempt(self, method: str, status: str):
        """Record authentication attempt"""
        AUTH_ATTEMPTS.labels(method=method, status=status).inc()

    def record_auth_success(self, method: str):
        """Record successful authentication"""
        AUTH_SUCCESS.labels(method=method).inc()

    def set_active_connections(self, count: int):
        """Set active connections count"""
        ACTIVE_CONNECTIONS.set(count)

    def set_database_connections(self, count: int):
        """Set database connections count"""
        DATABASE_CONNECTIONS.set(count)

    def set_redis_connections(self, count: int):
        """Set Redis connections count"""
        REDIS_CONNECTIONS.set(count)

    def get_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        return generate_latest(self.registry).decode("utf-8")

    def get_metrics_dict(self) -> Dict[str, Any]:
        """Get metrics as dictionary for JSON response"""
        # This would require custom implementation to convert Prometheus metrics to dict
        # For now, return basic info
        return {
            "registry": "prometheus",
            "metrics_count": len(list(self.registry.collect())),
            "timestamp": time.time(),
        }


# Global metrics collector instance
metrics_collector = MetricsCollector()
