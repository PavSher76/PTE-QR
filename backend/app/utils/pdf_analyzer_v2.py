"""
Полностью переработанный PDF анализатор для максимальной эффективности
Работает только с pdf_content в памяти, без временных файлов
"""

import structlog
import time
import psutil
from typing import Dict, Any, Tuple, Optional, List, Union
from PyPDF2 import PdfReader
from PIL import Image
import io
from io import BytesIO
import fitz  # PyMuPDF
import numpy as np
from app.core.config import settings
from app.utils.pdf_exceptions import (
    PDFAnalysisError, PDFFileError, PDFCorruptedError, PDFPageError, 
    PDFPageOutOfRangeError, PDFPageCorruptedError, PDFImageProcessingError,
    PDFOpenCVError, PDFCoordinateError, PDFAnalysisTimeoutError, 
    PDFMemoryError, PDFDependencyError, PDFConfigurationError,
    PDFAnalysisWarning, PDFPerformanceWarning
)

# Try to import OpenCV and scikit-image, fallback to basic functionality if not available
try:
    import cv2
    from scipy import ndimage
    from skimage import measure, morphology
    CV_AVAILABLE = True
    CV_VERSION = cv2.__version__
    SCIPY_VERSION = ndimage.__version__ if hasattr(ndimage, '__version__') else "unknown"
except ImportError as e:
    logger = structlog.get_logger()
    logger.warning(f"OpenCV/scikit-image not available: {e}. Using fallback mode.")
    CV_AVAILABLE = False
    CV_VERSION = None
    SCIPY_VERSION = None
    
    import warnings
    warnings.warn(
        PDFDependencyError(
            f"OpenCV/scikit-image not available: {e}. Using fallback mode.",
            missing_dependency="opencv-python",
            fallback_used=True
        )
    )


class PDFAnalyzerV2:
    """
    Полностью переработанный PDF анализатор
    - Работает только с pdf_content в памяти
    - Максимальная производительность
    - Улучшенная отладка
    - Без временных файлов
    """
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        self.analysis_timeout = 30.0
        self.max_memory_usage = 1024 * 1024 * 1024  # 1GB
        
        # Кэш для анализа
        self._analysis_cache = {}
        self._image_cache = {}
        
        # Статистика анализа
        self.analysis_stats = {
            "total_analyses": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "fallback_analyses": 0,
            "cache_hits": 0,
            "average_analysis_time": 0.0,
            "memory_usage_history": []
        }
        
        # Конфигурация анализа
        self.analysis_config = {
            "stamp_detection_area_width_cm": 20.0,
            "stamp_detection_area_height_cm": 10.0,
            "min_line_length_cm": 15.0,
            "qr_size_cm": 3.5,
            "margin_cm": 0.5,
            "image_scale_factor": 2.0,
            "canny_low_threshold": 30,
            "canny_high_threshold": 100,
            "min_contour_area": 100,
            "max_contour_area": 100000
        }
    
    def _check_system_resources(self) -> None:
        """Проверка доступности системных ресурсов"""
        try:
            memory = psutil.virtual_memory()
            available_memory = memory.available
            
            if available_memory < self.max_memory_usage:
                raise PDFMemoryError(
                    f"Insufficient memory for PDF analysis. Available: {available_memory / (1024*1024):.1f}MB, Required: {self.max_memory_usage / (1024*1024):.1f}MB",
                    required_memory=self.max_memory_usage,
                    available_memory=available_memory
                )
            
            cpu_percent = psutil.cpu_percent(interval=0.1)
            if cpu_percent > 90:
                import warnings
                warnings.warn(
                    PDFPerformanceWarning(
                        f"High CPU usage detected: {cpu_percent:.1f}%. PDF analysis may be slow.",
                        performance_metric="cpu_usage",
                        metric_value=cpu_percent
                    )
                )
                
        except Exception as e:
            self.logger.warning("Failed to check system resources", error=str(e))
    
    def _validate_pdf_content(self, pdf_content: bytes) -> None:
        """Валидация содержимого PDF"""
        if not pdf_content:
            raise PDFFileError("PDF content is empty", file_size=0)
        
        if len(pdf_content) < 100:
            raise PDFFileError(
                f"PDF file is too small: {len(pdf_content)} bytes. Minimum size is 100 bytes.",
                file_size=len(pdf_content)
            )
        
        if not pdf_content.startswith(b'%PDF'):
            raise PDFCorruptedError(
                "Invalid PDF file format. File does not start with PDF signature.",
                corruption_type="invalid_signature"
            )
        
        if b'%%EOF' not in pdf_content[-1000:]:
            raise PDFCorruptedError(
                "PDF file appears to be truncated. EOF marker not found.",
                corruption_type="truncated_file"
            )
    
    def _validate_page_number(self, page_number: int, total_pages: int) -> None:
        """Валидация номера страницы"""
        if page_number < 0:
            raise PDFPageError(
                f"Page number cannot be negative: {page_number}",
                page_number=page_number,
                total_pages=total_pages
            )
        
        if page_number >= total_pages:
            raise PDFPageOutOfRangeError(page_number, total_pages)
    
    def _check_analysis_timeout(self, start_time: float, stage: str) -> None:
        """Проверка таймаута анализа"""
        elapsed_time = time.time() - start_time
        if elapsed_time > self.analysis_timeout:
            raise PDFAnalysisTimeoutError(
                f"PDF analysis timed out after {elapsed_time:.1f} seconds during {stage}",
                timeout_seconds=elapsed_time,
                analysis_stage=stage
            )
    
    def _get_page_image(self, pdf_content: bytes, page_number: int) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Получение изображения страницы и метаданных из PDF содержимого
        """
        cache_key = f"page_image_{hash(pdf_content)}_{page_number}"
        
        if cache_key in self._image_cache:
            self.analysis_stats["cache_hits"] += 1
            return self._image_cache[cache_key]
        
        try:
            # Открываем PDF с помощью PyMuPDF
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            if page_number >= len(doc):
                raise PDFPageOutOfRangeError(page_number, len(doc))
            
            page = doc[page_number]
            
            # Получаем метаданные страницы
            page_metadata = {
                "width": float(page.rect.width),
                "height": float(page.rect.height),
                "rotation": getattr(page, 'rotation', 0) % 360,
                "mediabox": {
                    "x0": float(page.mediabox[0]),
                    "y0": float(page.mediabox[1]),
                    "x1": float(page.mediabox[2]),
                    "y1": float(page.mediabox[3])
                }
            }
            
            # Конвертируем страницу в изображение
            scale_factor = self.analysis_config["image_scale_factor"]
            mat = fitz.Matrix(scale_factor, scale_factor)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Конвертируем в numpy array
            pil_image = Image.open(io.BytesIO(img_data))
            img_array = np.array(pil_image.convert('L'))
            
            result = (img_array, page_metadata)
            
            # Кэшируем результат
            self._image_cache[cache_key] = result
            
            # Ограничиваем размер кэша
            if len(self._image_cache) > 50:
                # Удаляем самые старые записи
                oldest_key = next(iter(self._image_cache))
                del self._image_cache[oldest_key]
            
            doc.close()
            return result
            
        except Exception as e:
            raise PDFImageProcessingError(
                f"Failed to get page image: {str(e)}",
                page_number=page_number,
                processing_stage="image_conversion"
            )
    
    def _detect_stamp_in_region(self, img_array: np.ndarray, page_metadata: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """
        Детекция штампа в области поиска
        """
        if not CV_AVAILABLE:
            return self._fallback_stamp_detection(page_metadata)
        
        try:
            page_width = page_metadata["width"]
            page_height = page_metadata["height"]
            
            # Проверяем landscape ориентацию
            if page_width <= page_height:
                self.logger.debug("Skipping stamp detection for portrait page")
                return None
            
            # Определяем область поиска штампа
            scale_factor = self.analysis_config["image_scale_factor"]
            stamp_width_pixels = int(self.analysis_config["stamp_detection_area_width_cm"] * 28.35 * scale_factor)
            stamp_height_pixels = int(self.analysis_config["stamp_detection_area_height_cm"] * 28.35 * scale_factor)
            
            right_start = max(0, img_array.shape[1] - stamp_width_pixels)
            bottom_start = max(0, img_array.shape[0] - stamp_height_pixels)
            
            stamp_region = img_array[bottom_start:, right_start:]
            
            # Применяем детекцию краев
            edges = cv2.Canny(
                stamp_region, 
                self.analysis_config["canny_low_threshold"],
                self.analysis_config["canny_high_threshold"]
            )
            
            # Ищем контуры
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Фильтруем контуры
            stamp_contours = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < self.analysis_config["min_contour_area"]:
                    continue
                
                epsilon = 0.05 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                if len(approx) >= 4:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if 0.3 < aspect_ratio < 5.0:
                        stamp_contours.append((contour, x, y, w, h))
            
            if not stamp_contours:
                return None
            
            # Выбираем лучший контур
            def stamp_score(contour_data):
                _, x, y, w, h = contour_data
                area = w * h
                aspect_ratio = w / h
                
                position_score = 0
                if x > stamp_region.shape[1] * 0.6:
                    position_score += 4
                if y > stamp_region.shape[0] * 0.4:
                    position_score += 4
                
                aspect_score = 0
                if 1.5 < aspect_ratio < 4.0:
                    aspect_score += 3
                elif 1.0 < aspect_ratio < 6.0:
                    aspect_score += 1
                
                size_score = 0
                if 1000 < area < 50000:
                    size_score += 2
                elif 500 < area < 100000:
                    size_score += 1
                
                return position_score + aspect_score + size_score
            
            stamp_contours.sort(key=stamp_score, reverse=True)
            _, x, y, w, h = stamp_contours[0]
            
            # Конвертируем координаты в PDF точки
            actual_x = right_start + x
            actual_y = bottom_start + y
            stamp_top_y = actual_y - h
            
            x_img_points = actual_x / scale_factor
            y_img_points = stamp_top_y / scale_factor
            
            x_pdf, y_pdf = self._to_pdf_point(x_img_points, y_img_points, page_height)
            
            return {
                "x": x_pdf,
                "y": y_pdf,
                "width": w / scale_factor,
                "height": h / scale_factor,
                "confidence": stamp_score(stamp_contours[0]) / 10.0
            }
            
        except Exception as e:
            self.logger.warning("Error during stamp detection", error=str(e))
            return self._fallback_stamp_detection(page_metadata)
    
    def _detect_frame_edges(self, img_array: np.ndarray, page_metadata: Dict[str, Any]) -> Dict[str, Optional[float]]:
        """
        Детекция краев рамки
        """
        if not CV_AVAILABLE:
            return {
                "right_edge": self._fallback_frame_detection(page_metadata, "right"),
                "bottom_edge": self._fallback_frame_detection(page_metadata, "bottom")
            }
        
        try:
            page_width = page_metadata["width"]
            page_height = page_metadata["height"]
            scale_factor = self.analysis_config["image_scale_factor"]
            
            # Детекция правого края
            right_region_width = int(page_width * 0.2 * scale_factor)
            right_region = img_array[:, -right_region_width:]
            
            edges = cv2.Canny(right_region, 50, 150)
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
            vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
            
            contours, _ = cv2.findContours(vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            rightmost_x = 0
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if h > img_array.shape[0] * 0.3:
                    rightmost_x = max(rightmost_x, x + w)
            
            right_edge = None
            if rightmost_x > 0:
                actual_x = (img_array.shape[1] - right_region_width) + rightmost_x
                x_img_points = actual_x / scale_factor
                right_edge = x_img_points
            
            # Детекция нижнего края
            bottom_region_height = int(page_height * 0.2 * scale_factor)
            bottom_region = img_array[-bottom_region_height:, :]
            
            edges = cv2.Canny(bottom_region, 50, 150)
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
            horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
            
            contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            bottommost_y = 0
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > img_array.shape[1] * 0.3:
                    bottommost_y = max(bottommost_y, y + h)
            
            bottom_edge = None
            if bottommost_y > 0:
                actual_y = (img_array.shape[0] - bottom_region_height) + bottommost_y
                y_img_points = actual_y / scale_factor
                x_pdf, y_pdf = self._to_pdf_point(0, y_img_points, page_height)
                bottom_edge = y_pdf
            
            return {
                "right_edge": right_edge,
                "bottom_edge": bottom_edge
            }
            
        except Exception as e:
            self.logger.warning("Error during frame edge detection", error=str(e))
            return {
                "right_edge": self._fallback_frame_detection(page_metadata, "right"),
                "bottom_edge": self._fallback_frame_detection(page_metadata, "bottom")
            }
    
    def _detect_horizontal_lines(self, img_array: np.ndarray, page_metadata: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """
        Детекция горизонтальных линий
        """
        if not CV_AVAILABLE:
            return self._fallback_horizontal_line_detection(page_metadata)
        
        try:
            page_height = page_metadata["height"]
            scale_factor = self.analysis_config["image_scale_factor"]
            
            # Ищем в верхней части страницы
            top_region_height = int(page_height * 0.3 * scale_factor)
            top_region = img_array[:top_region_height, :]
            
            edges = cv2.Canny(top_region, 30, 100)
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 1))
            horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
            
            contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            min_length_pixels = int(self.analysis_config["min_line_length_cm"] * 28.35 * scale_factor)
            
            valid_lines = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                if w >= min_length_pixels and h <= 5:
                    line_length_cm = w / (28.35 * scale_factor)
                    valid_lines.append({
                        "start_x": x,
                        "end_x": x + w,
                        "y": y,
                        "length_cm": line_length_cm
                    })
            
            if not valid_lines:
                return None
            
            # Выбираем самую нижнюю линию
            valid_lines.sort(key=lambda line: line["y"], reverse=True)
            best_line = valid_lines[0]
            
            # Конвертируем координаты
            scale_factor = self.analysis_config["image_scale_factor"]
            x_img_points = best_line["start_x"] / scale_factor
            y_img_points = best_line["y"] / scale_factor
            
            x_pdf, y_pdf = self._to_pdf_point(x_img_points, y_img_points, page_height)
            
            return {
                "start_x": best_line["start_x"] / scale_factor,
                "end_x": best_line["end_x"] / scale_factor,
                "y": y_pdf,
                "length_cm": best_line["length_cm"]
            }
            
        except Exception as e:
            self.logger.warning("Error during horizontal line detection", error=str(e))
            return self._fallback_horizontal_line_detection(page_metadata)
    
    def _calculate_qr_position(self, page_metadata: Dict[str, Any], detected_elements: Dict[str, Any]) -> Dict[str, float]:
        """
        Расчет позиции QR кода на основе обнаруженных элементов
        """
        try:
            page_width = page_metadata["width"]
            page_height = page_metadata["height"]
            
            qr_size_points = self.analysis_config["qr_size_cm"] * 28.35
            margin_points = self.analysis_config["margin_cm"] * 28.35
            
            # Приоритетная логика позиционирования
            if detected_elements.get("stamp") and detected_elements["stamp"].get("confidence", 0) > 0.5:
                # Позиционируем относительно штампа
                stamp = detected_elements["stamp"]
                x_position = stamp["x"] - qr_size_points - margin_points
                y_position = stamp["y"] - qr_size_points - margin_points
                
            elif detected_elements.get("right_edge") and detected_elements.get("bottom_edge"):
                # Позиционируем относительно рамки
                x_position = detected_elements["right_edge"] - qr_size_points - margin_points
                y_position = detected_elements["bottom_edge"] + margin_points
                
            elif detected_elements.get("horizontal_line"):
                # Позиционируем относительно горизонтальной линии
                line = detected_elements["horizontal_line"]
                x_position = line["end_x"] - qr_size_points - margin_points
                y_position = line["y"] - qr_size_points - margin_points
                
            else:
                # Fallback: используем якорь
                anchor = settings.QR_ANCHOR
                if anchor == 'bottom-right':
                    x_position = page_width - qr_size_points - margin_points
                    y_position = margin_points
                elif anchor == 'bottom-left':
                    x_position = margin_points
                    y_position = margin_points
                elif anchor == 'top-right':
                    x_position = page_width - qr_size_points - margin_points
                    y_position = page_height - qr_size_points - margin_points
                else:  # top-left
                    x_position = margin_points
                    y_position = page_height - qr_size_points - margin_points
            
            # Клэмп координат
            x_position = max(0, min(x_position, page_width - qr_size_points))
            y_position = max(0, min(y_position, page_height - qr_size_points))
            
            return {
                "x": x_position,
                "y": y_position,
                "width": qr_size_points,
                "height": qr_size_points
            }
            
        except Exception as e:
            self.logger.warning("Error calculating QR position", error=str(e))
            # Fallback позиция
            page_width = page_metadata["width"]
            page_height = page_metadata["height"]
            qr_size_points = self.analysis_config["qr_size_cm"] * 28.35
            margin_points = self.analysis_config["margin_cm"] * 28.35
            
            return {
                "x": page_width - qr_size_points - margin_points,
                "y": margin_points,
                "width": qr_size_points,
                "height": qr_size_points
            }
    
    def _to_pdf_point(self, x_img: float, y_img: float, page_h: float) -> Tuple[float, float]:
        """Конвертация координат из image-СК в PDF-СК"""
        x_pdf = x_img
        y_pdf = page_h - y_img
        return x_pdf, y_pdf
    
    def _fallback_stamp_detection(self, page_metadata: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """Fallback детекция штампа"""
        try:
            page_height = page_metadata["height"]
            estimated_y = page_height * 0.1
            
            return {
                "x": 0,
                "y": estimated_y,
                "width": 100,
                "height": 50,
                "confidence": 0.1
            }
        except Exception:
            return None
    
    def _fallback_frame_detection(self, page_metadata: Dict[str, Any], frame_type: str) -> Optional[float]:
        """Fallback детекция рамки"""
        try:
            if frame_type == "right":
                return page_metadata["width"] * 0.95
            elif frame_type == "bottom":
                return page_metadata["height"] * 0.05
            return None
        except Exception:
            return None
    
    def _fallback_horizontal_line_detection(self, page_metadata: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """Fallback детекция горизонтальной линии"""
        try:
            page_width = page_metadata["width"]
            page_height = page_metadata["height"]
            
            return {
                "start_x": page_width * 0.1,
                "end_x": page_width * 0.9,
                "y": page_height * 0.9,
                "length_cm": (page_width * 0.8) / 28.35
            }
        except Exception:
            return None
    
    def _update_analysis_stats(self, success: bool, analysis_time: float, fallback_used: bool = False) -> None:
        """Обновление статистики анализа"""
        self.analysis_stats["total_analyses"] += 1
        
        if success:
            self.analysis_stats["successful_analyses"] += 1
        else:
            self.analysis_stats["failed_analyses"] += 1
        
        if fallback_used:
            self.analysis_stats["fallback_analyses"] += 1
        
        # Обновляем среднее время анализа
        total_successful = self.analysis_stats["successful_analyses"]
        if total_successful > 0:
            current_avg = self.analysis_stats["average_analysis_time"]
            self.analysis_stats["average_analysis_time"] = (
                (current_avg * (total_successful - 1) + analysis_time) / total_successful
            )
        
        # Записываем использование памяти
        try:
            memory_usage = psutil.Process().memory_info().rss
            self.analysis_stats["memory_usage_history"].append({
                "timestamp": time.time(),
                "memory_mb": memory_usage / (1024 * 1024)
            })
            
            if len(self.analysis_stats["memory_usage_history"]) > 100:
                self.analysis_stats["memory_usage_history"] = self.analysis_stats["memory_usage_history"][-100:]
                
        except Exception as e:
            self.logger.warning("Failed to record memory usage", error=str(e))
    
    def analyze_page_layout(self, pdf_content: bytes, page_number: int = 0) -> Dict[str, Any]:
        """
        Основной метод анализа макета страницы
        """
        start_time = time.time()
        analysis_success = False
        fallback_used = False
        
        try:
            self.logger.debug("Starting page layout analysis", 
                            page_number=page_number, 
                            content_size=len(pdf_content))
            
            # Проверка системных ресурсов
            self._check_system_resources()
            
            # Валидация входных данных
            self._validate_pdf_content(pdf_content)
            
            # Получаем изображение страницы
            img_array, page_metadata = self._get_page_image(pdf_content, page_number)
            
            # Валидация номера страницы
            self._validate_page_number(page_number, 1)  # Уже проверили в _get_page_image
            
            # Проверка таймаута
            self._check_analysis_timeout(start_time, "page_validation")
            
            # Определяем ориентацию страницы
            is_landscape = page_metadata["width"] > page_metadata["height"]
            
            # Анализируем элементы страницы
            detected_elements = {}
            
            # Детекция штампа (только для landscape)
            if is_landscape:
                try:
                    self._check_analysis_timeout(start_time, "stamp_detection")
                    stamp = self._detect_stamp_in_region(img_array, page_metadata)
                    if stamp:
                        detected_elements["stamp"] = stamp
                except Exception as e:
                    self.logger.warning("Error during stamp detection", error=str(e))
                    fallback_used = True
            
            # Детекция краев рамки
            try:
                self._check_analysis_timeout(start_time, "frame_detection")
                frame_edges = self._detect_frame_edges(img_array, page_metadata)
                if frame_edges["right_edge"]:
                    detected_elements["right_edge"] = frame_edges["right_edge"]
                if frame_edges["bottom_edge"]:
                    detected_elements["bottom_edge"] = frame_edges["bottom_edge"]
            except Exception as e:
                self.logger.warning("Error during frame detection", error=str(e))
                fallback_used = True
            
            # Детекция горизонтальных линий
            try:
                self._check_analysis_timeout(start_time, "line_detection")
                horizontal_line = self._detect_horizontal_lines(img_array, page_metadata)
                if horizontal_line:
                    detected_elements["horizontal_line"] = horizontal_line
            except Exception as e:
                self.logger.warning("Error during line detection", error=str(e))
                fallback_used = True
            
            # Расчет позиции QR кода
            try:
                self._check_analysis_timeout(start_time, "qr_positioning")
                qr_position = self._calculate_qr_position(page_metadata, detected_elements)
                detected_elements["qr_position"] = qr_position
            except Exception as e:
                self.logger.warning("Error during QR positioning", error=str(e))
                fallback_used = True
            
            # Формируем результат
            analysis_time = time.time() - start_time
            
            result = {
                "page_number": page_number,
                "page_width": page_metadata["width"],
                "page_height": page_metadata["height"],
                "rotation": page_metadata["rotation"],
                "is_landscape": is_landscape,
                "detected_elements": detected_elements,
                "analysis_metadata": {
                    "analysis_time": analysis_time,
                    "fallback_used": fallback_used,
                    "cv_available": CV_AVAILABLE,
                    "cache_hit": cache_key in self._image_cache if 'cache_key' in locals() else False,
                    "elements_found": {
                        "stamp": "stamp" in detected_elements,
                        "right_edge": "right_edge" in detected_elements,
                        "bottom_edge": "bottom_edge" in detected_elements,
                        "horizontal_line": "horizontal_line" in detected_elements,
                        "qr_position": "qr_position" in detected_elements
                    }
                }
            }
            
            analysis_success = True
            
            self.logger.info("Page layout analysis completed successfully", 
                           page_number=page_number,
                           is_landscape=is_landscape,
                           analysis_time=analysis_time,
                           fallback_used=fallback_used,
                           elements_found=result["analysis_metadata"]["elements_found"])
            
            return result
            
        except (PDFFileError, PDFCorruptedError, PDFPageError, PDFPageOutOfRangeError, 
                PDFPageCorruptedError, PDFMemoryError, PDFAnalysisTimeoutError) as e:
            # Специфичные ошибки PDF анализа
            analysis_time = time.time() - start_time
            self.logger.error("PDF analysis failed with specific error", 
                            error_type=type(e).__name__,
                            error_code=getattr(e, 'error_code', 'UNKNOWN'),
                            error_message=str(e),
                            page_number=page_number,
                            analysis_time=analysis_time,
                            error_details=getattr(e, 'details', {}))
            
            self._update_analysis_stats(False, analysis_time, fallback_used)
            raise
            
        except Exception as e:
            # Общие ошибки
            analysis_time = time.time() - start_time
            self.logger.error("PDF analysis failed with unexpected error", 
                            error=str(e),
                            error_type=type(e).__name__,
                            page_number=page_number,
                            analysis_time=analysis_time,
                            exc_info=True)
            
            self._update_analysis_stats(False, analysis_time, fallback_used)
            raise PDFAnalysisError(
                f"Unexpected error during PDF analysis: {str(e)}",
                details={"original_error": str(e), "error_type": type(e).__name__}
            )
            
        finally:
            # Обновляем статистику
            analysis_time = time.time() - start_time
            self._update_analysis_stats(analysis_success, analysis_time, fallback_used)
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Получение статистики анализа"""
        return {
            **self.analysis_stats,
            "cv_available": CV_AVAILABLE,
            "cv_version": CV_VERSION,
            "scipy_version": SCIPY_VERSION,
            "analysis_timeout": self.analysis_timeout,
            "max_memory_usage_mb": self.max_memory_usage / (1024 * 1024),
            "cache_size": len(self._image_cache),
            "analysis_config": self.analysis_config
        }
    
    def clear_cache(self):
        """Очистка кэша"""
        self._analysis_cache.clear()
        self._image_cache.clear()
        self.logger.debug("Analysis cache cleared")
    
    def update_config(self, config_updates: Dict[str, Any]) -> None:
        """Обновление конфигурации анализа"""
        self.analysis_config.update(config_updates)
        self.logger.info("Analysis configuration updated", config_updates=config_updates)
