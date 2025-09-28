"""
Система отладки и мониторинга для PDF анализа
"""

import structlog
import time
import json
import os
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from collections import defaultdict, deque


class DebugLevel(Enum):
    """Уровни отладки"""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class DebugEvent:
    """Событие отладки"""
    timestamp: float
    level: DebugLevel
    component: str
    message: str
    data: Dict[str, Any]
    thread_id: int
    operation_id: Optional[str] = None


@dataclass
class PerformanceMetric:
    """Метрика производительности"""
    operation_name: str
    start_time: float
    end_time: float
    duration: float
    memory_before: int
    memory_after: int
    memory_delta: int
    success: bool
    error_message: Optional[str] = None


class DebugSystem:
    """
    Система отладки и мониторинга
    """
    
    def __init__(self, max_events: int = 10000, max_metrics: int = 1000):
        self.logger = structlog.get_logger(__name__)
        self.max_events = max_events
        self.max_metrics = max_metrics
        
        # Хранилище событий
        self.events: deque = deque(maxlen=max_events)
        self.metrics: deque = deque(maxlen=max_metrics)
        
        # Счетчики
        self.counters: Dict[str, int] = defaultdict(int)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        
        # Активные операции
        self.active_operations: Dict[str, Dict[str, Any]] = {}
        
        # Блокировка для потокобезопасности
        self.lock = threading.Lock()
        
        # Конфигурация
        self.config = {
            "enable_tracing": True,
            "enable_metrics": True,
            "enable_counters": True,
            "log_level": DebugLevel.INFO,
            "auto_cleanup_interval": 3600,  # 1 час
            "max_operation_time": 300,  # 5 минут
        }
        
        # Запускаем автоочистку
        self._start_auto_cleanup()
    
    def log_event(self, level: DebugLevel, component: str, message: str, 
                  data: Dict[str, Any] = None, operation_id: str = None):
        """Логирование события"""
        if not self.config["enable_tracing"]:
            return
        
        if level.value < self.config["log_level"].value:
            return
        
        event = DebugEvent(
            timestamp=time.time(),
            level=level,
            component=component,
            message=message,
            data=data or {},
            thread_id=threading.get_ident(),
            operation_id=operation_id
        )
        
        with self.lock:
            self.events.append(event)
        
        # Логируем в structlog
        log_data = {
            "level": level.value,
            "component": component,
            "data": data or {},
            "operation_id": operation_id
        }
        
        if level == DebugLevel.TRACE:
            self.logger.trace(message, **log_data)
        elif level == DebugLevel.DEBUG:
            self.logger.debug(message, **log_data)
        elif level == DebugLevel.INFO:
            self.logger.info(message, **log_data)
        elif level == DebugLevel.WARNING:
            self.logger.warning(message, **log_data)
        elif level == DebugLevel.ERROR:
            self.logger.error(message, **log_data)
        elif level == DebugLevel.CRITICAL:
            self.logger.critical(message, **log_data)
    
    def start_operation(self, operation_name: str, operation_id: str = None) -> str:
        """Начало операции"""
        if not operation_id:
            operation_id = f"{operation_name}_{int(time.time() * 1000)}"
        
        import psutil
        process = psutil.Process()
        
        operation_data = {
            "name": operation_name,
            "start_time": time.time(),
            "memory_before": process.memory_info().rss,
            "thread_id": threading.get_ident()
        }
        
        with self.lock:
            self.active_operations[operation_id] = operation_data
        
        self.log_event(
            DebugLevel.INFO,
            "operation",
            f"Started operation: {operation_name}",
            {"operation_id": operation_id},
            operation_id
        )
        
        return operation_id
    
    def end_operation(self, operation_id: str, success: bool = True, 
                      error_message: str = None):
        """Завершение операции"""
        with self.lock:
            if operation_id not in self.active_operations:
                self.log_event(
                    DebugLevel.WARNING,
                    "operation",
                    f"Operation {operation_id} not found in active operations"
                )
                return
            
            operation_data = self.active_operations.pop(operation_id)
        
        import psutil
        process = psutil.Process()
        
        end_time = time.time()
        duration = end_time - operation_data["start_time"]
        memory_after = process.memory_info().rss
        memory_delta = memory_after - operation_data["memory_before"]
        
        metric = PerformanceMetric(
            operation_name=operation_data["name"],
            start_time=operation_data["start_time"],
            end_time=end_time,
            duration=duration,
            memory_before=operation_data["memory_before"],
            memory_after=memory_after,
            memory_delta=memory_delta,
            success=success,
            error_message=error_message
        )
        
        if self.config["enable_metrics"]:
            with self.lock:
                self.metrics.append(metric)
                self.timers[operation_data["name"]].append(duration)
        
        # Обновляем счетчики
        if self.config["enable_counters"]:
            with self.lock:
                self.counters[f"{operation_data['name']}_total"] += 1
                if success:
                    self.counters[f"{operation_data['name']}_success"] += 1
                else:
                    self.counters[f"{operation_data['name']}_failed"] += 1
        
        level = DebugLevel.INFO if success else DebugLevel.ERROR
        self.log_event(
            level,
            "operation",
            f"Completed operation: {operation_data['name']}",
            {
                "operation_id": operation_id,
                "duration": duration,
                "memory_delta": memory_delta,
                "success": success,
                "error_message": error_message
            },
            operation_id
        )
    
    def increment_counter(self, counter_name: str, value: int = 1):
        """Увеличение счетчика"""
        if not self.config["enable_counters"]:
            return
        
        with self.lock:
            self.counters[counter_name] += value
    
    def get_events(self, component: str = None, level: DebugLevel = None, 
                   since: float = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение событий"""
        with self.lock:
            events = list(self.events)
        
        # Фильтрация
        if component:
            events = [e for e in events if e.component == component]
        
        if level:
            events = [e for e in events if e.level == level]
        
        if since:
            events = [e for e in events if e.timestamp >= since]
        
        # Сортировка по времени (новые первыми)
        events.sort(key=lambda e: e.timestamp, reverse=True)
        
        # Ограничение
        events = events[:limit]
        
        return [asdict(event) for event in events]
    
    def get_metrics(self, operation_name: str = None, since: float = None, 
                    limit: int = 100) -> List[Dict[str, Any]]:
        """Получение метрик"""
        with self.lock:
            metrics = list(self.metrics)
        
        # Фильтрация
        if operation_name:
            metrics = [m for m in metrics if m.operation_name == operation_name]
        
        if since:
            metrics = [m for m in metrics if m.start_time >= since]
        
        # Сортировка по времени (новые первыми)
        metrics.sort(key=lambda m: m.start_time, reverse=True)
        
        # Ограничение
        metrics = metrics[:limit]
        
        return [asdict(metric) for metric in metrics]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики"""
        with self.lock:
            events = list(self.events)
            metrics = list(self.metrics)
            counters = dict(self.counters)
            timers = {name: list(times) for name, times in self.timers.items()}
        
        # Статистика событий
        event_stats = {}
        for event in events:
            level = event.level.value
            component = event.component
            if level not in event_stats:
                event_stats[level] = {}
            if component not in event_stats[level]:
                event_stats[level][component] = 0
            event_stats[level][component] += 1
        
        # Статистика метрик
        metric_stats = {}
        for metric in metrics:
            name = metric.operation_name
            if name not in metric_stats:
                metric_stats[name] = {
                    "total": 0,
                    "success": 0,
                    "failed": 0,
                    "avg_duration": 0.0,
                    "min_duration": float('inf'),
                    "max_duration": 0.0,
                    "avg_memory_delta": 0.0
                }
            
            stats = metric_stats[name]
            stats["total"] += 1
            if metric.success:
                stats["success"] += 1
            else:
                stats["failed"] += 1
            
            stats["avg_duration"] = (stats["avg_duration"] * (stats["total"] - 1) + metric.duration) / stats["total"]
            stats["min_duration"] = min(stats["min_duration"], metric.duration)
            stats["max_duration"] = max(stats["max_duration"], metric.duration)
            stats["avg_memory_delta"] = (stats["avg_memory_delta"] * (stats["total"] - 1) + metric.memory_delta) / stats["total"]
        
        # Статистика таймеров
        timer_stats = {}
        for name, times in timers.items():
            if times:
                timer_stats[name] = {
                    "count": len(times),
                    "avg": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                    "p95": sorted(times)[int(len(times) * 0.95)] if len(times) > 1 else times[0]
                }
        
        return {
            "events": {
                "total": len(events),
                "by_level": event_stats,
                "recent_count": len([e for e in events if e.timestamp > time.time() - 3600])
            },
            "metrics": {
                "total": len(metrics),
                "by_operation": metric_stats
            },
            "counters": counters,
            "timers": timer_stats,
            "active_operations": len(self.active_operations),
            "config": self.config
        }
    
    def export_data(self, filepath: str):
        """Экспорт данных отладки"""
        data = {
            "events": [asdict(event) for event in self.events],
            "metrics": [asdict(metric) for metric in self.metrics],
            "counters": dict(self.counters),
            "statistics": self.get_statistics(),
            "export_time": time.time()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        self.log_event(
            DebugLevel.INFO,
            "debug_system",
            f"Exported debug data to {filepath}",
            {"filepath": filepath, "events_count": len(data["events"])}
        )
    
    def clear_data(self):
        """Очистка данных отладки"""
        with self.lock:
            self.events.clear()
            self.metrics.clear()
            self.counters.clear()
            self.timers.clear()
            self.active_operations.clear()
        
        self.log_event(
            DebugLevel.INFO,
            "debug_system",
            "Cleared all debug data"
        )
    
    def _start_auto_cleanup(self):
        """Запуск автоочистки"""
        def cleanup_worker():
            while True:
                time.sleep(self.config["auto_cleanup_interval"])
                self._cleanup_old_data()
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def _cleanup_old_data(self):
        """Очистка старых данных"""
        cutoff_time = time.time() - (24 * 3600)  # 24 часа назад
        
        with self.lock:
            # Очищаем старые события
            self.events = deque(
                [e for e in self.events if e.timestamp > cutoff_time],
                maxlen=self.max_events
            )
            
            # Очищаем старые метрики
            self.metrics = deque(
                [m for m in self.metrics if m.start_time > cutoff_time],
                maxlen=self.max_metrics
            )
            
            # Очищаем зависшие операции
            current_time = time.time()
            for op_id, op_data in list(self.active_operations.items()):
                if current_time - op_data["start_time"] > self.config["max_operation_time"]:
                    del self.active_operations[op_id]
                    self.log_event(
                        DebugLevel.WARNING,
                        "debug_system",
                        f"Cleaned up stuck operation: {op_data['name']}",
                        {"operation_id": op_id}
                    )
    
    def update_config(self, config_updates: Dict[str, Any]):
        """Обновление конфигурации"""
        self.config.update(config_updates)
        self.log_event(
            DebugLevel.INFO,
            "debug_system",
            "Updated debug system configuration",
            {"config_updates": config_updates}
        )


# Глобальный экземпляр системы отладки
debug_system = DebugSystem()


def debug_trace(component: str, message: str, data: Dict[str, Any] = None, operation_id: str = None):
    """Трассировка"""
    debug_system.log_event(DebugLevel.TRACE, component, message, data, operation_id)


def debug_info(component: str, message: str, data: Dict[str, Any] = None, operation_id: str = None):
    """Информация"""
    debug_system.log_event(DebugLevel.INFO, component, message, data, operation_id)


def debug_warning(component: str, message: str, data: Dict[str, Any] = None, operation_id: str = None):
    """Предупреждение"""
    debug_system.log_event(DebugLevel.WARNING, component, message, data, operation_id)


def debug_error(component: str, message: str, data: Dict[str, Any] = None, operation_id: str = None):
    """Ошибка"""
    debug_system.log_event(DebugLevel.ERROR, component, message, data, operation_id)


def debug_operation(operation_name: str, operation_id: str = None):
    """Декоратор для отслеживания операций"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            op_id = debug_system.start_operation(operation_name, operation_id)
            try:
                result = func(*args, **kwargs)
                debug_system.end_operation(op_id, success=True)
                return result
            except Exception as e:
                debug_system.end_operation(op_id, success=False, error_message=str(e))
                raise
        return wrapper
    return decorator
