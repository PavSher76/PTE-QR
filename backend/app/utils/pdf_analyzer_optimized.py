"""
Оптимизированный PDF analyzer для детекции позиций штампов и рамок
Устранены проблемы с временными файлами и неиспользуемым кодом
"""

import structlog
from typing import Dict, Any, Tuple, Optional, List
from PyPDF2 import PdfReader
from PIL import Image
import io
from io import BytesIO
import fitz  # PyMuPDF
import numpy as np
from app.core.config import settings

# Try to import OpenCV and scikit-image, fallback to basic functionality if not available
try:
    import cv2
    from scipy import ndimage
    from skimage import measure, morphology
    CV_AVAILABLE = True
except ImportError as e:
    structlog.get_logger().warning(f"OpenCV/scikit-image not available: {e}. Using fallback mode.")
    CV_AVAILABLE = False

class OptimizedPDFAnalyzer:
    """Оптимизированный PDF analyzer для детекции позиций штампов и рамок"""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        # Кэш для избежания повторных вычислений
        self._analysis_cache = {}
    
    def to_pdf_point(self, x_img: float, y_img: float, page_h: float) -> Tuple[float, float]:
        """
        Конвертирует точку из image-СК (origin верх-лево) в PDF-СК (origin низ-лево)
        """
        x_pdf = x_img
        y_pdf = page_h - y_img
        return x_pdf, y_pdf
    
    def to_pdf_bbox(self, x_img: float, y_img: float, obj_w: float, obj_h: float, page_h: float) -> Tuple[float, float, float, float]:
        """
        Конвертирует bbox из image-СК (origin верх-лево) в PDF-СК (origin низ-лево)
        """
        x_pdf = x_img
        y_pdf = page_h - (y_img + obj_h)
        return x_pdf, y_pdf, obj_w, obj_h
    
    def _audit_page_coordinates(self, page, page_number: int = 0) -> Dict[str, Any]:
        """
        Аудит координат и юнитов страницы PDF
        """
        try:
            # Получаем различные боксы страницы
            mediabox = page.mediabox
            cropbox = page.cropbox if hasattr(page, 'cropbox') else None
            rotation = getattr(page, 'rotation', 0) % 360
            
            # Основные размеры
            mediabox_width = float(mediabox.width)
            mediabox_height = float(mediabox.height)
            
            # CropBox (если есть)
            cropbox_info = None
            if cropbox:
                cropbox_width = float(cropbox.width)
                cropbox_height = float(cropbox.height)
                cropbox_info = {
                    "width": cropbox_width,
                    "height": cropbox_height,
                    "x0": float(cropbox[0]),  # left
                    "y0": float(cropbox[1]),  # bottom
                    "x1": float(cropbox[2]),  # right
                    "y1": float(cropbox[3])   # top
                }
            
            # Определяем какой бокс использовать для позиционирования
            position_box = settings.QR_POSITION_BOX.lower()
            if position_box == "crop" and cropbox_info:
                active_box = cropbox_info
                active_box_type = "cropbox"
            else:
                active_box = {
                    "width": mediabox_width,
                    "height": mediabox_height,
                    "x0": float(mediabox[0]),  # left
                    "y0": float(mediabox[1]),  # bottom
                    "x1": float(mediabox[2]),  # right
                    "y1": float(mediabox[3])   # top
                }
                active_box_type = "mediabox"
            
            coordinate_info = {
                "page_number": page_number,
                "rotation": rotation,
                "mediabox": {
                    "width": mediabox_width,
                    "height": mediabox_height,
                    "x0": float(mediabox[0]),
                    "y0": float(mediabox[1]),
                    "x1": float(mediabox[2]),
                    "y1": float(mediabox[3])
                },
                "cropbox": cropbox_info,
                "active_box": active_box,
                "active_box_type": active_box_type,
                "coordinate_system": {
                    "origin": "bottom-left",
                    "units": "points (pt)",
                    "note": "PDF standard coordinate system"
                },
                "orientation": "landscape" if mediabox_width > mediabox_height else "portrait",
                "aspect_ratio": mediabox_width / mediabox_height,
                "config": {
                    "position_box": position_box,
                    "respect_rotation": settings.QR_RESPECT_ROTATION
                }
            }
            
            return coordinate_info
            
        except Exception as e:
            self.logger.error("❌ Error auditing page coordinates", 
                            error=str(e), page_number=page_number)
            return {}
    
    def compute_simple_anchor(self, page_box: Dict[str, float], qr_size: float, margin: float = None, 
                             anchor: str = None) -> Tuple[float, float]:
        """
        Жёсткий расчет позиции QR кода по якорю без учета поворота
        """
        try:
            width = page_box["width"]
            height = page_box["height"]
            
            # Используем значения из конфига если не указаны
            if margin is None:
                margin = settings.QR_MARGIN_PT
            if anchor is None:
                anchor = settings.QR_ANCHOR
            
            # Жёсткая геометрия для разных якорей
            if anchor == 'bottom-right':
                x = width - qr_size - margin
                y = margin
            elif anchor == 'bottom-left':
                x = margin
                y = margin
            elif anchor == 'top-right':
                x = width - qr_size - margin
                y = height - qr_size - margin
            elif anchor == 'top-left':
                x = margin
                y = height - qr_size - margin
            else:
                self.logger.warning(f"Unknown anchor '{anchor}', using 'bottom-right'")
                x = width - qr_size - margin
                y = margin
            
            # Клэмп координат
            x = max(0, min(x, width - qr_size))
            y = max(0, min(y, height - qr_size))
            
            return x, y
            
        except Exception as e:
            self.logger.error("❌ Error computing hard anchor", 
                            error=str(e), anchor=anchor)
            # Fallback к bottom-right с клэмпом
            width = page_box["width"]
            height = page_box["height"]
            x = max(0, min(width - qr_size - margin, width - qr_size))
            y = max(0, min(margin, height - qr_size))
            return x, y

    def compute_qr_anchor(self, page_box: Dict[str, float], qr_size: float, margin: float = None, 
                         anchor: str = None, rotation: int = 0) -> Tuple[float, float]:
        """
        Унифицированный расчет позиции QR кода с учетом якоря и поворота
        """
        try:
            # Сначала вычисляем жёсткую геометрию якоря
            base_x, base_y = self.compute_simple_anchor(page_box, qr_size, margin, anchor)
            
            # Нормализуем поворот
            rotation = rotation % 360
            
            # Проверяем, нужно ли учитывать поворот
            if not settings.QR_RESPECT_ROTATION:
                rotation = 0
            
            width = page_box["width"]
            height = page_box["height"]
            
            # Применяем поворот по правильной таблице
            if rotation == 0:
                final_x, final_y = base_x, base_y
            elif rotation == 90:
                final_x = margin
                final_y = margin
            elif rotation == 180:
                final_x = margin
                final_y = height - margin - qr_size
            elif rotation == 270:
                final_x = width - margin - qr_size
                final_y = height - margin - qr_size
            else:
                self.logger.warning(f"Unsupported rotation {rotation}, using 0°")
                final_x, final_y = base_x, base_y
            
            # Клэмп координат после поворота
            final_x = max(0, min(final_x, width - qr_size))
            final_y = max(0, min(final_y, height - qr_size))
            
            return final_x, final_y
            
        except Exception as e:
            self.logger.error("❌ Error computing QR anchor", 
                            error=str(e), anchor=anchor, rotation=rotation)
            # Fallback к жёсткому якорю без поворота
            return self.compute_simple_anchor(page_box, qr_size, margin, anchor)
    
    def analyze_page_layout_optimized(self, pdf_content: bytes, page_number: int = 0) -> Dict[str, Any]:
        """
        Оптимизированный анализ макета страницы без создания временных файлов
        
        Args:
            pdf_content: Содержимое PDF файла в байтах
            page_number: Номер страницы (начиная с 0)
            
        Returns:
            Словарь с информацией о макете страницы
        """
        try:
            # Проверяем кэш
            cache_key = f"{hash(pdf_content)}_{page_number}"
            if cache_key in self._analysis_cache:
                self.logger.debug("Using cached analysis result", page_number=page_number)
                return self._analysis_cache[cache_key]
            
            self.logger.debug("Analyzing page layout (optimized)", page_number=page_number)
            
            # Открываем PDF с помощью PyMuPDF (fitz) для анализа изображения
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            if page_number >= len(doc):
                self.logger.error("Page number out of range", 
                                page_number=page_number, total_pages=len(doc))
                return {}
                
            page = doc[page_number]
            
            # Аудит координат страницы
            coordinate_info = self._audit_page_coordinates(page, page_number)
            
            # Определяем ориентацию страницы
            is_landscape = coordinate_info["orientation"] == "landscape"
            
            result = {
                "page_number": page_number,
                "page_width": coordinate_info["active_box"]["width"],
                "page_height": coordinate_info["active_box"]["height"],
                "rotation": coordinate_info["rotation"],
                "is_landscape": is_landscape,
                "coordinate_info": coordinate_info,
                "stamp_top_edge": None,
                "right_frame_edge": None,
                "bottom_frame_edge": None,
                "horizontal_line_18cm": None,
                "free_space_3_5cm": None
            }
            
            # Анализируем страницу напрямую без временных файлов
            if CV_AVAILABLE:
                # Для landscape страниц определяем верхний край штампа
                if is_landscape:
                    result["stamp_top_edge"] = self._detect_stamp_top_edge_optimized(page, page_number)
                
                # Определяем элементы страницы
                result["right_frame_edge"] = self._detect_right_frame_edge_optimized(page, page_number)
                result["bottom_frame_edge"] = self._detect_bottom_frame_edge_optimized(page, page_number)
                result["horizontal_line_18cm"] = self._detect_horizontal_line_optimized(page, page_number)
                result["free_space_3_5cm"] = self._detect_free_space_optimized(page, page_number)
            else:
                # Fallback режим без OpenCV
                self.logger.warning("OpenCV not available, using fallback analysis")
                result = self._fallback_analysis(page, page_number, coordinate_info)
            
            # Кэшируем результат
            self._analysis_cache[cache_key] = result
            
            self.logger.info("Page layout analysis completed (optimized)", 
                           page_number=page_number,
                           is_landscape=is_landscape,
                           rotation=coordinate_info["rotation"])
            
            doc.close()
            return result
            
        except Exception as e:
            self.logger.error("Error analyzing page layout (optimized)", 
                            error=str(e), page_number=page_number)
            return {}
    
    def _detect_stamp_top_edge_optimized(self, page, page_number: int = 0) -> Optional[float]:
        """
        Оптимизированная детекция верхнего края штампа без временных файлов
        """
        try:
            # Конвертируем страницу в изображение с высоким разрешением
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Конвертируем в PIL Image
            pil_image = Image.open(io.BytesIO(img_data))
            img_array = np.array(pil_image.convert('L'))
            
            # Получаем размеры страницы
            page_width = page.rect.width
            page_height = page.rect.height
            
            # Проверяем, что страница в landscape ориентации
            if page_width <= page_height:
                self.logger.warning("⚠️ Page is not in landscape orientation")
                return None
            
            # Ищем штамп в правом нижнем углу листа
            stamp_detection_area_width_cm = 20.0
            stamp_detection_area_height_cm = 10.0
            stamp_width_pixels = int(stamp_detection_area_width_cm * 28.35 * 2.0)
            stamp_height_pixels = int(stamp_detection_area_height_cm * 28.35 * 2.0)
            
            # Определяем область поиска в правом нижнем углу
            right_start = max(0, img_array.shape[1] - stamp_width_pixels)
            bottom_start = max(0, img_array.shape[0] - stamp_height_pixels)
            
            # Извлекаем область поиска штампа
            stamp_region = img_array[bottom_start:, right_start:]
            
            # Применяем детекцию краев для поиска прямоугольных областей
            edges = cv2.Canny(stamp_region, 30, 100)
            
            # Ищем контуры
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Фильтруем контуры по размеру и форме
            stamp_contours = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 100:
                    continue
                    
                epsilon = 0.05 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                if len(approx) >= 4:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if 0.3 < aspect_ratio < 5.0:
                        stamp_contours.append((contour, x, y, w, h))
            
            if not stamp_contours:
                self.logger.warning("❌ No stamp contours found on landscape page")
                return None
            
            # Выбираем контур, который наиболее вероятно является штампом
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
            
            # Сортируем по оценке штампа
            stamp_contours.sort(key=stamp_score, reverse=True)
            
            # Берем контур с наивысшей оценкой
            _, x, y, w, h = stamp_contours[0]
            
            # Конвертируем координаты обратно в PDF точки
            actual_x = right_start + x
            actual_y = bottom_start + y
            stamp_top_y = actual_y - h
            
            # Конвертируем из пикселей изображения в PDF точки
            scale_factor = 2.0
            x_img_points = actual_x / scale_factor
            y_img_points = stamp_top_y / scale_factor
            
            x_pdf, y_pdf = self.to_pdf_point(x_img_points, y_img_points, page_height)
            stamp_top_y_points = y_pdf
            
            self.logger.info("✅ Stamp top edge detected successfully (optimized)", 
                           stamp_top_y_points=stamp_top_y_points)
            
            return stamp_top_y_points
            
        except Exception as e:
            self.logger.error("Error detecting stamp top edge (optimized)", 
                            error=str(e), page_number=page_number)
            return None
    
    def _detect_right_frame_edge_optimized(self, page, page_number: int = 0) -> Optional[float]:
        """
        Оптимизированная детекция правого края рамки без временных файлов
        """
        try:
            # Конвертируем страницу в изображение
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Конвертируем в PIL Image
            pil_image = Image.open(io.BytesIO(img_data))
            img_array = np.array(pil_image.convert('L'))
            
            # Получаем размеры страницы
            page_width = page.rect.width
            page_height = page.rect.height
            
            # Ищем вертикальные линии в правой части страницы
            right_region_width = int(page_width * 0.2)
            right_region = img_array[:, -right_region_width:]
            
            # Применяем детекцию краев
            edges = cv2.Canny(right_region, 50, 150)
            
            # Ищем вертикальные линии
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
            vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
            
            # Находим контуры вертикальных линий
            contours, _ = cv2.findContours(vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Ищем самую правую вертикальную линию
            rightmost_x = 0
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if h > img_array.shape[0] * 0.3:
                    rightmost_x = max(rightmost_x, x + w)
            
            if rightmost_x == 0:
                self.logger.warning("No right frame edge found")
                return None
            
            # Конвертируем координаты обратно в PDF точки
            actual_x = (img_array.shape[1] - right_region_width) + rightmost_x
            
            scale_factor = 2.0
            x_img_points = actual_x / scale_factor
            y_img_points = 0
            
            x_pdf, y_pdf = self.to_pdf_point(x_img_points, y_img_points, page_height)
            frame_right_x_points = x_pdf
            
            self.logger.info("Right frame edge detected (optimized)", 
                           frame_right_x_points=frame_right_x_points)
            
            return frame_right_x_points
            
        except Exception as e:
            self.logger.error("Error detecting right frame edge (optimized)", 
                            error=str(e), page_number=page_number)
            return None
    
    def _detect_bottom_frame_edge_optimized(self, page, page_number: int = 0) -> Optional[float]:
        """
        Оптимизированная детекция нижнего края рамки без временных файлов
        """
        try:
            # Конвертируем страницу в изображение
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Конвертируем в PIL Image
            pil_image = Image.open(io.BytesIO(img_data))
            img_array = np.array(pil_image.convert('L'))
            
            # Получаем размеры страницы
            page_width = page.rect.width
            page_height = page.rect.height
            
            # Ищем горизонтальные линии в нижней части страницы
            bottom_region_height = int(page_height * 0.2)
            bottom_region = img_array[-bottom_region_height:, :]
            
            # Применяем детекцию краев
            edges = cv2.Canny(bottom_region, 50, 150)
            
            # Ищем горизонтальные линии
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
            horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
            
            # Находим контуры горизонтальных линий
            contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Ищем самую нижнюю горизонтальную линию
            bottommost_y = 0
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > img_array.shape[1] * 0.3:
                    bottommost_y = max(bottommost_y, y + h)
            
            if bottommost_y == 0:
                self.logger.warning("No bottom frame edge found")
                return None
            
            # Конвертируем координаты обратно в PDF точки
            actual_y = (img_array.shape[0] - bottom_region_height) + bottommost_y
            
            scale_factor = 2.0
            x_img_points = 0
            y_img_points = actual_y / scale_factor
            
            x_pdf, y_pdf = self.to_pdf_point(x_img_points, y_img_points, page_height)
            frame_bottom_y_points = y_pdf
            
            self.logger.info("Bottom frame edge detected (optimized)", 
                           frame_bottom_y_points=frame_bottom_y_points)
            
            return frame_bottom_y_points
            
        except Exception as e:
            self.logger.error("Error detecting bottom frame edge (optimized)", 
                            error=str(e), page_number=page_number)
            return None
    
    def _detect_horizontal_line_optimized(self, page, page_number: int = 0) -> Optional[Dict[str, float]]:
        """
        Оптимизированная детекция горизонтальной линии без временных файлов
        """
        try:
            # Конвертируем страницу в изображение
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Конвертируем в PIL Image
            pil_image = Image.open(io.BytesIO(img_data))
            img_array = np.array(pil_image.convert('L'))
            
            # Получаем размеры страницы
            page_width = page.rect.width
            page_height = page.rect.height
            
            # Ищем горизонтальные линии в верхней части страницы
            top_region_height = int(page_height * 0.3)
            top_region = img_array[:top_region_height, :]
            
            # Применяем детекцию краев
            edges = cv2.Canny(top_region, 30, 100)
            
            # Ищем горизонтальные линии
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 1))
            horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
            
            # Находим контуры горизонтальных линий
            contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Минимальная длина линии: 15 см в пикселях
            min_length_pixels = int(15.0 * 28.35 * 2.0)
            
            # Ищем самую верхнюю горизонтальную линию длиной не менее 15 см
            valid_lines = []
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                if w >= min_length_pixels and h <= 5:
                    line_length_cm = w / (28.35 * 2.0)
                    
                    valid_lines.append({
                        "start_x": x,
                        "end_x": x + w,
                        "y": y,
                        "length_cm": line_length_cm
                    })
            
            if not valid_lines:
                self.logger.warning("❌ No horizontal line 15cm+ found in top area")
                return None
            
            # Сортируем линии по Y-позиции и выбираем самую нижнюю
            valid_lines.sort(key=lambda line: line["y"], reverse=True)
            best_line = valid_lines[0]
            
            # Конвертируем координаты обратно в PDF точки
            scale_factor = 2.0
            x_img_points = best_line["start_x"] / scale_factor
            y_img_points = best_line["y"] / scale_factor
            
            x_pdf, y_pdf = self.to_pdf_point(x_img_points, y_img_points, page_height)
            
            line_info = {
                "start_x": best_line["start_x"] / scale_factor,
                "end_x": best_line["end_x"] / scale_factor,
                "y": y_pdf,
                "length_cm": best_line["length_cm"]
            }
            
            self.logger.info("✅ Top horizontal line 15cm+ detected (optimized)", 
                           start_x=line_info["start_x"],
                           end_x=line_info["end_x"],
                           y=line_info["y"],
                           length_cm=line_info["length_cm"])
            
            return line_info
            
        except Exception as e:
            self.logger.error("❌ Error detecting top horizontal line 15cm+ (optimized)", 
                            error=str(e), page_number=page_number)
            return None
    
    def _detect_free_space_optimized(self, page, page_number: int = 0) -> Optional[Dict[str, float]]:
        """
        Оптимизированный поиск свободного места без временных файлов
        """
        try:
            # Размер QR кода
            qr_size_cm = 3.5
            qr_size_points = qr_size_cm * 28.35
            margin_cm = 0.5
            margin_points = margin_cm * 28.35
            
            # Получаем размеры страницы
            page_width = page.rect.width
            page_height = page.rect.height
            
            # Fallback: ставим QR на 1 см от правого края и 1 см от нижнего края
            x_position = page_width - qr_size_points - (1.0 * 28.35)
            y_position = page_height - qr_size_points - (1.0 * 28.35)
            
            result = {
                "x": x_position,
                "y": y_position,
                "width": qr_size_points,
                "height": qr_size_points
            }
            
            self.logger.info("✅ Free space detected (optimized fallback)", 
                           x=result["x"], y=result["y"],
                           x_cm=round(result["x"] / 28.35, 2),
                           y_cm=round(result["y"] / 28.35, 2))
            
            return result
            
        except Exception as e:
            self.logger.error("❌ Error detecting free space (optimized)", 
                            error=str(e), page_number=page_number)
            return None
    
    def _fallback_analysis(self, page, page_number: int, coordinate_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback анализ без OpenCV
        """
        try:
            page_width = coordinate_info["active_box"]["width"]
            page_height = coordinate_info["active_box"]["height"]
            is_landscape = coordinate_info["orientation"] == "landscape"
            
            result = {
                "page_number": page_number,
                "page_width": page_width,
                "page_height": page_height,
                "rotation": coordinate_info["rotation"],
                "is_landscape": is_landscape,
                "coordinate_info": coordinate_info,
                "stamp_top_edge": None,
                "right_frame_edge": None,
                "bottom_frame_edge": None,
                "horizontal_line_18cm": None,
                "free_space_3_5cm": None
            }
            
            # Простые эвристики без OpenCV
            if is_landscape:
                # Штамп обычно находится в нижней части страницы
                result["stamp_top_edge"] = page_height * 0.1
            
            # Правая рамка обычно находится на 5% от ширины страницы от правого края
            result["right_frame_edge"] = page_width * 0.95
            
            # Нижняя рамка обычно находится на 5% от высоты страницы от низа
            result["bottom_frame_edge"] = page_height * 0.05
            
            # Горизонтальная линия в верхней части
            result["horizontal_line_18cm"] = {
                "start_x": page_width * 0.1,
                "end_x": page_width * 0.9,
                "y": page_height * 0.9,
                "length_cm": (page_width * 0.8) / 28.35
            }
            
            # Свободное место для QR кода
            qr_size_points = 3.5 * 28.35
            result["free_space_3_5cm"] = {
                "x": page_width - qr_size_points - (1.0 * 28.35),
                "y": page_height - qr_size_points - (1.0 * 28.35),
                "width": qr_size_points,
                "height": qr_size_points
            }
            
            self.logger.info("✅ Fallback analysis completed", 
                           page_number=page_number,
                           is_landscape=is_landscape)
            
            return result
            
        except Exception as e:
            self.logger.error("❌ Error in fallback analysis", error=str(e))
            return {}
    
    def clear_cache(self):
        """Очистка кэша анализа"""
        self._analysis_cache.clear()
        self.logger.debug("Analysis cache cleared")
