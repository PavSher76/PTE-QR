"""
Metrics collection service
"""

import time
from typing import Any, Dict, List

import psutil
import structlog
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

from app.core.config import settings

logger = structlog.get_logger()


class MetricsService:
    """Metrics collection service"""

    def __init__(self):
        # API metrics
        self.api_requests_total = Counter(
            "pte_qr_api_requests_total",
            "Total number of API requests",
            ["method", "endpoint", "status_code"],
        )

        self.api_request_duration = Histogram(
            "pte_qr_api_request_duration_seconds",
            "API request duration in seconds",
            ["method", "endpoint"],
        )

        # QR Code metrics
        self.qr_codes_generated_total = Counter(
            "pte_qr_codes_generated_total",
            "Total number of QR codes generated",
            ["doc_uid", "revision"],
        )

        self.qr_codes_verified_total = Counter(
            "pte_qr_codes_verified_total",
            "Total number of QR codes verified",
            ["status"],
        )

        # Document metrics
        self.document_status_checks_total = Counter(
            "pte_qr_document_status_checks_total",
            "Total number of document status checks",
            ["doc_uid", "revision", "is_actual"],
        )

        # ENOVIA metrics
        self.enovia_requests_total = Counter(
            "pte_qr_enovia_requests_total",
            "Total number of ENOVIA API requests",
            ["endpoint", "status"],
        )

        self.enovia_request_duration = Histogram(
            "pte_qr_enovia_request_duration_seconds",
            "ENOVIA API request duration in seconds",
            ["endpoint"],
        )

        # Cache metrics
        self.cache_hits_total = Counter(
            "pte_qr_cache_hits_total", "Total number of cache hits", ["cache_type"]
        )

        self.cache_misses_total = Counter(
            "pte_qr_cache_misses_total", "Total number of cache misses", ["cache_type"]
        )

        # System metrics
        self.system_cpu_usage = Gauge(
            "pte_qr_system_cpu_usage_percent", "System CPU usage percentage"
        )

        self.system_memory_usage = Gauge(
            "pte_qr_system_memory_usage_percent", "System memory usage percentage"
        )

        self.system_disk_usage = Gauge(
            "pte_qr_system_disk_usage_percent", "System disk usage percentage"
        )

        # Application metrics
        self.active_connections = Gauge(
            "pte_qr_active_connections", "Number of active connections"
        )

        self.uptime_seconds = Gauge(
            "pte_qr_uptime_seconds", "Application uptime in seconds"
        )

        self.start_time = time.time()

    def record_api_request(
        self, method: str, endpoint: str, status_code: int, duration: float
    ):
        """Record API request metrics"""
        self.api_requests_total.labels(
            method=method, endpoint=endpoint, status_code=str(status_code)
        ).inc()

        self.api_request_duration.labels(method=method, endpoint=endpoint).observe(
            duration
        )

    def record_qr_code_generated(self, doc_uid: str, revision: str):
        """Record QR code generation"""
        self.qr_codes_generated_total.labels(doc_uid=doc_uid, revision=revision).inc()

    def record_qr_code_verified(self, status: str):
        """Record QR code verification"""
        self.qr_codes_verified_total.labels(status=status).inc()

    def record_document_status_check(
        self, doc_uid: str, revision: str, is_actual: bool
    ):
        """Record document status check"""
        self.document_status_checks_total.labels(
            doc_uid=doc_uid, revision=revision, is_actual=str(is_actual)
        ).inc()

    def record_enovia_request(self, endpoint: str, status: str, duration: float):
        """Record ENOVIA API request"""
        self.enovia_requests_total.labels(endpoint=endpoint, status=status).inc()

        self.enovia_request_duration.labels(endpoint=endpoint).observe(duration)

    def record_cache_hit(self, cache_type: str):
        """Record cache hit"""
        self.cache_hits_total.labels(cache_type=cache_type).inc()

    def record_cache_miss(self, cache_type: str):
        """Record cache miss"""
        self.cache_misses_total.labels(cache_type=cache_type).inc()

    def update_system_metrics(self):
        """Update system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_cpu_usage.set(cpu_percent)

            # Memory usage
            memory = psutil.virtual_memory()
            self.system_memory_usage.set(memory.percent)

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100
            self.system_disk_usage.set(disk_percent)

            # Uptime
            uptime = time.time() - self.start_time
            self.uptime_seconds.set(uptime)

        except Exception as e:
            logger.error("Failed to update system metrics", error=str(e))

    def get_metrics_prometheus(self) -> str:
        """Get metrics in Prometheus format"""
        self.update_system_metrics()
        return generate_latest()

    def get_metrics_dict(self) -> Dict[str, Any]:
        """Get metrics as dictionary"""
        self.update_system_metrics()

        return {
            "api": {
                "requests_total": self._get_counter_value(self.api_requests_total),
                "request_duration": self._get_histogram_value(
                    self.api_request_duration
                ),
            },
            "qr_codes": {
                "generated_total": self._get_counter_value(
                    self.qr_codes_generated_total
                ),
                "verified_total": self._get_counter_value(self.qr_codes_verified_total),
            },
            "documents": {
                "status_checks_total": self._get_counter_value(
                    self.document_status_checks_total
                )
            },
            "enovia": {
                "requests_total": self._get_counter_value(self.enovia_requests_total),
                "request_duration": self._get_histogram_value(
                    self.enovia_request_duration
                ),
            },
            "cache": {
                "hits_total": self._get_counter_value(self.cache_hits_total),
                "misses_total": self._get_counter_value(self.cache_misses_total),
            },
            "system": {
                "cpu_usage_percent": self.system_cpu_usage._value._value,
                "memory_usage_percent": self.system_memory_usage._value._value,
                "disk_usage_percent": self.system_disk_usage._value._value,
                "uptime_seconds": self.uptime_seconds._value._value,
            },
        }

    def _get_counter_value(self, counter: Counter) -> Dict[str, float]:
        """Get counter value as dictionary"""
        result = {}
        for metric in counter.collect():
            for sample in metric.samples:
                labels = "_".join([f"{k}_{v}" for k, v in sample.labels.items()])
                result[labels or "total"] = sample.value
        return result

    def _get_histogram_value(self, histogram: Histogram) -> Dict[str, Any]:
        """Get histogram value as dictionary"""
        result = {}
        for metric in histogram.collect():
            for sample in metric.samples:
                if sample.name.endswith("_sum"):
                    result["sum"] = sample.value
                elif sample.name.endswith("_count"):
                    result["count"] = sample.value
                elif sample.name.endswith("_bucket"):
                    bucket = sample.labels.get("le", "inf")
                    result[f"bucket_{bucket}"] = sample.value
        return result

    def get_health_metrics(self) -> Dict[str, Any]:
        """Get health-related metrics"""
        self.update_system_metrics()

        return {
            "status": "healthy",
            "uptime_seconds": self.uptime_seconds._value._value,
            "cpu_usage_percent": self.system_cpu_usage._value._value,
            "memory_usage_percent": self.system_memory_usage._value._value,
            "disk_usage_percent": self.system_disk_usage._value._value,
            "total_requests": sum(
                self._get_counter_value(self.api_requests_total).values()
            ),
            "total_qr_codes": sum(
                self._get_counter_value(self.qr_codes_generated_total).values()
            ),
        }


# Global metrics service instance
metrics_service = MetricsService()
