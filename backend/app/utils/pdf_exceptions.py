"""
Кастомные исключения для PDF анализа и обработки
"""

from typing import Optional, Dict, Any


class PDFAnalysisError(Exception):
    """Базовое исключение для ошибок анализа PDF"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "PDF_ANALYSIS_ERROR"
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


class PDFFileError(PDFAnalysisError):
    """Ошибки связанные с файлом PDF"""
    
    def __init__(self, message: str, file_path: str = None, file_size: int = None, details: Dict[str, Any] = None):
        super().__init__(message, "PDF_FILE_ERROR", details)
        self.file_path = file_path
        self.file_size = file_size
        if file_path:
            self.details["file_path"] = file_path
        if file_size:
            self.details["file_size"] = file_size


class PDFCorruptedError(PDFFileError):
    """PDF файл поврежден или имеет неверный формат"""
    
    def __init__(self, message: str = "PDF file is corrupted or has invalid format", 
                 file_path: str = None, corruption_type: str = None):
        details = {"corruption_type": corruption_type} if corruption_type else {}
        super().__init__(message, file_path, details=details)
        self.error_code = "PDF_CORRUPTED_ERROR"
        self.corruption_type = corruption_type


class PDFPageError(PDFAnalysisError):
    """Ошибки связанные с конкретной страницей PDF"""
    
    def __init__(self, message: str, page_number: int, total_pages: int = None, details: Dict[str, Any] = None):
        super().__init__(message, "PDF_PAGE_ERROR", details)
        self.page_number = page_number
        self.total_pages = total_pages
        self.details.update({
            "page_number": page_number,
            "total_pages": total_pages
        })


class PDFPageOutOfRangeError(PDFPageError):
    """Запрошенная страница находится вне диапазона"""
    
    def __init__(self, page_number: int, total_pages: int):
        message = f"Page {page_number} is out of range. Document has {total_pages} pages."
        super().__init__(message, page_number, total_pages)
        self.error_code = "PDF_PAGE_OUT_OF_RANGE"


class PDFPageCorruptedError(PDFPageError):
    """Страница PDF повреждена"""
    
    def __init__(self, page_number: int, corruption_reason: str = None):
        message = f"Page {page_number} is corrupted"
        if corruption_reason:
            message += f": {corruption_reason}"
        details = {"corruption_reason": corruption_reason} if corruption_reason else {}
        super().__init__(message, page_number, details=details)
        self.error_code = "PDF_PAGE_CORRUPTED"


class PDFImageProcessingError(PDFAnalysisError):
    """Ошибки обработки изображений PDF"""
    
    def __init__(self, message: str, page_number: int = None, processing_stage: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "PDF_IMAGE_PROCESSING_ERROR", details)
        self.page_number = page_number
        self.processing_stage = processing_stage
        if page_number:
            self.details["page_number"] = page_number
        if processing_stage:
            self.details["processing_stage"] = processing_stage


class PDFOpenCVError(PDFImageProcessingError):
    """Ошибки OpenCV при обработке изображений"""
    
    def __init__(self, message: str, opencv_operation: str = None, page_number: int = None):
        details = {"opencv_operation": opencv_operation} if opencv_operation else {}
        super().__init__(message, page_number, "opencv_processing", details)
        self.error_code = "PDF_OPENCV_ERROR"
        self.opencv_operation = opencv_operation


class PDFCoordinateError(PDFAnalysisError):
    """Ошибки работы с координатами PDF"""
    
    def __init__(self, message: str, coordinate_type: str = None, coordinates: Dict[str, float] = None, details: Dict[str, Any] = None):
        super().__init__(message, "PDF_COORDINATE_ERROR", details)
        self.coordinate_type = coordinate_type
        self.coordinates = coordinates
        if coordinate_type:
            self.details["coordinate_type"] = coordinate_type
        if coordinates:
            self.details["coordinates"] = coordinates


class PDFAnalysisTimeoutError(PDFAnalysisError):
    """Таймаут при анализе PDF"""
    
    def __init__(self, message: str, timeout_seconds: float = None, analysis_stage: str = None):
        details = {}
        if timeout_seconds:
            details["timeout_seconds"] = timeout_seconds
        if analysis_stage:
            details["analysis_stage"] = analysis_stage
        super().__init__(message, "PDF_ANALYSIS_TIMEOUT", details)
        self.timeout_seconds = timeout_seconds
        self.analysis_stage = analysis_stage


class PDFMemoryError(PDFAnalysisError):
    """Недостаточно памяти для обработки PDF"""
    
    def __init__(self, message: str, required_memory: int = None, available_memory: int = None, page_number: int = None):
        details = {}
        if required_memory:
            details["required_memory_mb"] = required_memory / (1024 * 1024)
        if available_memory:
            details["available_memory_mb"] = available_memory / (1024 * 1024)
        if page_number:
            details["page_number"] = page_number
        super().__init__(message, "PDF_MEMORY_ERROR", details)
        self.required_memory = required_memory
        self.available_memory = available_memory
        self.page_number = page_number


class PDFDependencyError(PDFAnalysisError):
    """Ошибки зависимостей (OpenCV, scikit-image и т.д.)"""
    
    def __init__(self, message: str, missing_dependency: str = None, fallback_used: bool = False):
        details = {}
        if missing_dependency:
            details["missing_dependency"] = missing_dependency
        details["fallback_used"] = fallback_used
        super().__init__(message, "PDF_DEPENDENCY_ERROR", details)
        self.missing_dependency = missing_dependency
        self.fallback_used = fallback_used


class PDFConfigurationError(PDFAnalysisError):
    """Ошибки конфигурации PDF анализа"""
    
    def __init__(self, message: str, config_parameter: str = None, config_value: Any = None):
        details = {}
        if config_parameter:
            details["config_parameter"] = config_parameter
        if config_value is not None:
            details["config_value"] = config_value
        super().__init__(message, "PDF_CONFIGURATION_ERROR", details)
        self.config_parameter = config_parameter
        self.config_value = config_value


class PDFAnalysisWarning(Warning):
    """Предупреждения при анализе PDF"""
    
    def __init__(self, message: str, warning_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.warning_code = warning_code or "PDF_ANALYSIS_WARNING"
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "warning_type": self.__class__.__name__,
            "warning_code": self.warning_code,
            "message": self.message,
            "details": self.details
        }


class PDFPerformanceWarning(PDFAnalysisWarning):
    """Предупреждения о производительности"""
    
    def __init__(self, message: str, performance_metric: str = None, metric_value: float = None):
        details = {}
        if performance_metric:
            details["performance_metric"] = performance_metric
        if metric_value is not None:
            details["metric_value"] = metric_value
        super().__init__(message, "PDF_PERFORMANCE_WARNING", details)
        self.performance_metric = performance_metric
        self.metric_value = metric_value
