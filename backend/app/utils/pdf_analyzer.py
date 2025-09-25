"""
PDF analyzer for detecting stamp and frame positions
"""

import structlog
from typing import Dict, Any, Tuple, Optional
from PyPDF2 import PdfReader
from PIL import Image
import io
import fitz  # PyMuPDF
import numpy as np

# Try to import OpenCV and scikit-image, fallback to basic functionality if not available
try:
    import cv2
    from scipy import ndimage
    from skimage import measure, morphology
    CV_AVAILABLE = True
except ImportError as e:
    structlog.get_logger().warning(f"OpenCV/scikit-image not available: {e}. Using fallback mode.")
    CV_AVAILABLE = False

class PDFAnalyzer:
    """PDF analyzer for detecting stamp and frame positions"""
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        
    def detect_stamp_top_edge_landscape(self, pdf_path: str, page_number: int = 0) -> Optional[float]:
        """
        Определяет верхний край штампа основной надписи на landscape странице
        
        Args:
            pdf_path: Путь к PDF файлу
            page_number: Номер страницы (начиная с 0)
            
        Returns:
            Y-координата верхнего края штампа в точках PDF, или None если не найден
        """
        if not CV_AVAILABLE:
            self.logger.warning("OpenCV not available, using fallback stamp detection")
            return self._fallback_stamp_detection(pdf_path, page_number)
            
        try:
            self.logger.debug("🔍 Starting stamp detection for landscape page", 
                            pdf_path=pdf_path, page_number=page_number)
            
            # Открываем PDF с помощью PyMuPDF для анализа изображения
            doc = fitz.open(pdf_path)
            if page_number >= len(doc):
                self.logger.error("❌ Page number out of range", 
                                page_number=page_number, total_pages=len(doc))
                return None
                
            page = doc[page_number]
            
            # Получаем размеры страницы
            page_rect = page.rect
            page_width = page_rect.width
            page_height = page_rect.height
            
            self.logger.debug("📄 Page dimensions", 
                            page_width=page_width, page_height=page_height,
                            aspect_ratio=page_width/page_height)
            
            # Проверяем, что страница в landscape ориентации
            if page_width <= page_height:
                self.logger.warning("⚠️ Page is not in landscape orientation", 
                                  page_width=page_width, page_height=page_height,
                                  aspect_ratio=page_width/page_height)
                return None
            
            # Конвертируем страницу в изображение с высоким разрешением
            mat = fitz.Matrix(2.0, 2.0)  # Увеличиваем разрешение в 2 раза
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            self.logger.debug("🖼️ Image conversion", 
                            matrix_scale=2.0, 
                            pixmap_size=(pix.width, pix.height))
            
            # Конвертируем в PIL Image
            pil_image = Image.open(io.BytesIO(img_data))
            img_array = np.array(pil_image.convert('L'))  # Конвертируем в grayscale
            
            self.logger.debug("📊 Image processing", 
                            original_size=(pil_image.width, pil_image.height),
                            grayscale_shape=img_array.shape,
                            pixel_range=(img_array.min(), img_array.max()))
            
            # Ищем штамп в правом нижнем углу листа в области 20 см по горизонтали и 8 см по вертикали
            # Увеличили область для учета отступов от края листа до рамки (0.5+ мм) + толщина рамки
            # Конвертируем см в пиксели (1 см = 28.35 точек, масштаб 2.0)
            stamp_width_cm = 20.0  # Увеличили с 15 до 20 см для учета отступов и рамки
            stamp_height_cm = 8.0  # Увеличили с 6 до 8 см для учета отступов и рамки
            stamp_width_pixels = int(stamp_width_cm * 28.35 * 2.0)  # 20 см в пикселях
            stamp_height_pixels = int(stamp_height_cm * 28.35 * 2.0)  # 8 см в пикселях
            
            # Определяем область поиска в правом нижнем углу
            right_start = max(0, img_array.shape[1] - stamp_width_pixels)
            bottom_start = max(0, img_array.shape[0] - stamp_height_pixels)
            
            # Извлекаем область поиска штампа
            stamp_region = img_array[bottom_start:, right_start:]
            
            self.logger.debug("🔍 Stamp region analysis", 
                            total_height=img_array.shape[0],
                            total_width=img_array.shape[1],
                            stamp_region_height=stamp_region.shape[0],
                            stamp_region_width=stamp_region.shape[1],
                            stamp_width_cm=stamp_width_cm,
                            stamp_height_cm=stamp_height_cm,
                            right_start=right_start,
                            bottom_start=bottom_start)
            
            # Применяем детекцию краев для поиска прямоугольных областей
            # Используем более мягкие параметры для лучшей детекции
            edges = cv2.Canny(stamp_region, 30, 100)
            
            self.logger.debug("🔍 Edge detection", 
                            canny_low=30, canny_high=100,
                            edges_shape=edges.shape,
                            edges_nonzero=np.count_nonzero(edges),
                            edges_percentage=np.count_nonzero(edges) / edges.size * 100)
            
            # Ищем контуры
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            self.logger.debug("📐 Contour detection", 
                            total_contours=len(contours))
            
            # Фильтруем контуры по размеру и форме (ищем прямоугольные области)
            stamp_contours = []
            filtered_contours = []
            
            for i, contour in enumerate(contours):
                # Вычисляем площадь контура
                area = cv2.contourArea(contour)
                if area < 100:  # Еще больше уменьшили минимальную площадь
                    filtered_contours.append(f"contour_{i}: area={area:.0f} (too small)")
                    continue
                    
                # Аппроксимируем контур с более мягкими параметрами
                epsilon = 0.05 * cv2.arcLength(contour, True)  # Увеличили epsilon
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Проверяем, что это прямоугольник (4 угла) или близко к нему
                if len(approx) >= 4:  # Разрешаем больше углов
                    # Проверяем соотношение сторон (штамп обычно не очень широкий)
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if 0.3 < aspect_ratio < 5.0:  # Расширили диапазон соотношений
                        stamp_contours.append((contour, x, y, w, h))
                        filtered_contours.append(f"contour_{i}: area={area:.0f}, bbox=({x},{y},{w},{h}), aspect={aspect_ratio:.2f}, corners={len(approx)} ✅")
                    else:
                        filtered_contours.append(f"contour_{i}: area={area:.0f}, bbox=({x},{y},{w},{h}), aspect={aspect_ratio:.2f} (bad aspect)")
                else:
                    filtered_contours.append(f"contour_{i}: area={area:.0f}, corners={len(approx)} (not rectangular)")
            
            self.logger.debug("🔍 Contour filtering", 
                            valid_stamp_contours=len(stamp_contours),
                            filtered_details=filtered_contours[:20])  # Показываем первые 20
            
            if not stamp_contours:
                self.logger.warning("❌ No stamp contours found on landscape page")
                return None
            
            # Выбираем контур, который наиболее вероятно является штампом
            # Приоритет: 1) Позиция (правый нижний угол), 2) Размер, 3) Соотношение сторон
            def stamp_score(contour_data):
                _, x, y, w, h = contour_data
                area = w * h
                aspect_ratio = w / h
                
                # Бонус за позицию в правом нижнем углу области поиска
                position_score = 0
                if x > stamp_region.shape[1] * 0.6:  # В правой части области поиска (увеличили с 0.5 до 0.6)
                    position_score += 4  # Увеличили бонус
                if y > stamp_region.shape[0] * 0.4:  # В нижней части области поиска (увеличили с 0.3 до 0.4)
                    position_score += 4  # Увеличили бонус
                
                # Бонус за подходящее соотношение сторон (штамп обычно не очень широкий)
                aspect_score = 0
                if 1.5 < aspect_ratio < 4.0:  # Оптимальное соотношение для штампа
                    aspect_score += 3
                elif 1.0 < aspect_ratio < 6.0:  # Приемлемое соотношение
                    aspect_score += 1
                
                # Бонус за размер (не слишком маленький, не слишком большой)
                size_score = 0
                if 1000 < area < 50000:  # Оптимальный размер
                    size_score += 2
                elif 500 < area < 100000:  # Приемлемый размер
                    size_score += 1
                
                total_score = position_score + aspect_score + size_score
                return total_score
            
            # Сортируем по оценке штампа
            stamp_contours.sort(key=stamp_score, reverse=True)
            
            self.logger.debug("📊 Stamp selection", 
                            total_candidates=len(stamp_contours),
                            areas=[x[3] * x[4] for x in stamp_contours])
            
            # Берем контур с наивысшей оценкой
            _, x, y, w, h = stamp_contours[0]
            
            # Логируем детали выбора штампа
            selected_score = stamp_score(stamp_contours[0])
            self.logger.debug("🎯 Selected stamp", 
                            bbox=(x, y, w, h),
                            area=w * h,
                            aspect_ratio=w / h,
                            score=selected_score)
            
            # Логируем топ-3 кандидатов для отладки
            top_candidates = []
            for i, (_, cx, cy, cw, ch) in enumerate(stamp_contours[:3]):
                score = stamp_score(stamp_contours[i])
                top_candidates.append(f"#{i+1}: bbox=({cx},{cy},{cw},{ch}), area={cw*ch}, aspect={cw/ch:.2f}, score={score}")
            
            self.logger.debug("🏆 Top stamp candidates", 
                            candidates=top_candidates)
            
            # Конвертируем координаты обратно в PDF точки
            # x, y - это координаты относительно области поиска штампа
            # Нужно пересчитать относительно всей страницы
            actual_x = right_start + x
            actual_y = bottom_start + y
            stamp_top_y = actual_y - h  # Верхний край штампа
            
            # Конвертируем из пикселей изображения в PDF точки
            # Учитываем масштаб (mat = 2.0)
            scale_factor = 2.0
            stamp_top_y_points = (img_array.shape[0] - stamp_top_y) / scale_factor
            
            self.logger.debug("🔄 Coordinate conversion", 
                            right_start=right_start,
                            bottom_start=bottom_start,
                            actual_x=actual_x,
                            actual_y=actual_y,
                            stamp_top_y=stamp_top_y,
                            scale_factor=scale_factor,
                            final_y_points=stamp_top_y_points)
            
            self.logger.info("✅ Stamp top edge detected successfully", 
                           stamp_top_y_points=stamp_top_y_points,
                           stamp_bbox=(x, y, w, h),
                           confidence="high" if len(stamp_contours) == 1 else "medium")
            
            doc.close()
            return stamp_top_y_points
            
        except Exception as e:
            self.logger.error("Error detecting stamp top edge", 
                            error=str(e), pdf_path=pdf_path, page_number=page_number)
            return None
    
    def detect_right_frame_edge(self, pdf_path: str, page_number: int = 0) -> Optional[float]:
        """
        Определяет край рамки на правой стороне листа
        
        Args:
            pdf_path: Путь к PDF файлу
            page_number: Номер страницы (начиная с 0)
            
        Returns:
            X-координата правого края рамки в точках PDF, или None если не найден
        """
        if not CV_AVAILABLE:
            self.logger.warning("OpenCV not available, using fallback frame detection")
            return self._fallback_frame_detection(pdf_path, page_number, "right")
            
        try:
            self.logger.debug("Detecting right frame edge", 
                            pdf_path=pdf_path, page_number=page_number)
            
            # Открываем PDF с помощью PyMuPDF
            doc = fitz.open(pdf_path)
            if page_number >= len(doc):
                self.logger.error("Page number out of range", 
                                page_number=page_number, total_pages=len(doc))
                return None
                
            page = doc[page_number]
            
            # Получаем размеры страницы
            page_rect = page.rect
            page_width = page_rect.width
            page_height = page_rect.height
            
            # Конвертируем страницу в изображение
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Конвертируем в PIL Image
            pil_image = Image.open(io.BytesIO(img_data))
            img_array = np.array(pil_image.convert('L'))
            
            # Ищем вертикальные линии в правой части страницы
            right_region_width = int(page_width * 0.2)  # Правые 20% страницы
            right_region = img_array[:, -right_region_width:]
            
            # Применяем детекцию краев
            edges = cv2.Canny(right_region, 50, 150)
            
            # Ищем вертикальные линии
            # Используем морфологические операции для выделения вертикальных линий
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15))
            vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
            
            # Находим контуры вертикальных линий
            contours, _ = cv2.findContours(vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Ищем самую правую вертикальную линию
            rightmost_x = 0
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                # Проверяем, что это достаточно длинная вертикальная линия
                if h > img_array.shape[0] * 0.3:  # Линия должна быть не менее 30% высоты страницы
                    rightmost_x = max(rightmost_x, x + w)
            
            if rightmost_x == 0:
                self.logger.warning("No right frame edge found")
                doc.close()
                return None
            
            # Конвертируем координаты обратно в PDF точки
            # rightmost_x - это координата относительно правой области
            actual_x = (img_array.shape[1] - right_region_width) + rightmost_x
            frame_right_x_points = actual_x / 2.0  # Учитываем масштаб
            
            self.logger.info("Right frame edge detected", 
                           frame_right_x_points=frame_right_x_points,
                           rightmost_x=rightmost_x)
            
            doc.close()
            return frame_right_x_points
            
        except Exception as e:
            self.logger.error("Error detecting right frame edge", 
                            error=str(e), pdf_path=pdf_path, page_number=page_number)
            return None
    
    def detect_bottom_frame_edge(self, pdf_path: str, page_number: int = 0) -> Optional[float]:
        """
        Определяет край нижней рамки листа
        
        Args:
            pdf_path: Путь к PDF файлу
            page_number: Номер страницы (начиная с 0)
            
        Returns:
            Y-координата нижнего края рамки в точках PDF, или None если не найден
        """
        if not CV_AVAILABLE:
            self.logger.warning("OpenCV not available, using fallback frame detection")
            return self._fallback_frame_detection(pdf_path, page_number, "bottom")
            
        try:
            self.logger.debug("Detecting bottom frame edge", 
                            pdf_path=pdf_path, page_number=page_number)
            
            # Открываем PDF с помощью PyMuPDF
            doc = fitz.open(pdf_path)
            if page_number >= len(doc):
                self.logger.error("Page number out of range", 
                                page_number=page_number, total_pages=len(doc))
                return None
                
            page = doc[page_number]
            
            # Получаем размеры страницы
            page_rect = page.rect
            page_width = page_rect.width
            page_height = page_rect.height
            
            # Конвертируем страницу в изображение
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Конвертируем в PIL Image
            pil_image = Image.open(io.BytesIO(img_data))
            img_array = np.array(pil_image.convert('L'))
            
            # Ищем горизонтальные линии в нижней части страницы
            bottom_region_height = int(page_height * 0.2)  # Нижние 20% страницы
            bottom_region = img_array[-bottom_region_height:, :]
            
            # Применяем детекцию краев
            edges = cv2.Canny(bottom_region, 50, 150)
            
            # Ищем горизонтальные линии
            # Используем морфологические операции для выделения горизонтальных линий
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))
            horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
            
            # Находим контуры горизонтальных линий
            contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Ищем самую нижнюю горизонтальную линию
            bottommost_y = 0
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                # Проверяем, что это достаточно длинная горизонтальная линия
                if w > img_array.shape[1] * 0.3:  # Линия должна быть не менее 30% ширины страницы
                    bottommost_y = max(bottommost_y, y + h)
            
            if bottommost_y == 0:
                self.logger.warning("No bottom frame edge found")
                doc.close()
                return None
            
            # Конвертируем координаты обратно в PDF точки
            # bottommost_y - это координата относительно нижней области
            actual_y = (img_array.shape[0] - bottom_region_height) + bottommost_y
            frame_bottom_y_points = (img_array.shape[0] - actual_y) / 2.0  # Учитываем масштаб
            
            self.logger.info("Bottom frame edge detected", 
                           frame_bottom_y_points=frame_bottom_y_points,
                           bottommost_y=bottommost_y)
            
            doc.close()
            return frame_bottom_y_points
            
        except Exception as e:
            self.logger.error("Error detecting bottom frame edge", 
                            error=str(e), pdf_path=pdf_path, page_number=page_number)
            return None
    
    def analyze_page_layout(self, pdf_path: str, page_number: int = 0) -> Dict[str, Any]:
        """
        Анализирует макет страницы и возвращает информацию о позициях элементов
        
        Args:
            pdf_path: Путь к PDF файлу
            page_number: Номер страницы (начиная с 0)
            
        Returns:
            Словарь с информацией о макете страницы
        """
        try:
            self.logger.debug("Analyzing page layout", 
                            pdf_path=pdf_path, page_number=page_number)
            
            # Открываем PDF
            doc = fitz.open(pdf_path)
            if page_number >= len(doc):
                self.logger.error("Page number out of range", 
                                page_number=page_number, total_pages=len(doc))
                return {}
                
            page = doc[page_number]
            page_rect = page.rect
            
            # Определяем ориентацию страницы
            is_landscape = page_rect.width > page_rect.height
            
            result = {
                "page_number": page_number,
                "page_width": page_rect.width,
                "page_height": page_rect.height,
                "is_landscape": is_landscape,
                "stamp_top_edge": None,
                "right_frame_edge": None,
                "bottom_frame_edge": None
            }
            
            # Для landscape страниц определяем верхний край штампа
            stamp_top = None
            if is_landscape:
                stamp_top = self.detect_stamp_top_edge_landscape(pdf_path, page_number)
                result["stamp_top_edge"] = stamp_top
            
            # Определяем правый край рамки для всех страниц
            right_frame = self.detect_right_frame_edge(pdf_path, page_number)
            result["right_frame_edge"] = right_frame
            
            # Определяем нижний край рамки для всех страниц
            bottom_frame = self.detect_bottom_frame_edge(pdf_path, page_number)
            result["bottom_frame_edge"] = bottom_frame
            
            self.logger.info("Page layout analysis completed", 
                           page_number=page_number,
                           is_landscape=is_landscape,
                           stamp_top_edge=stamp_top,
                           right_frame_edge=right_frame)
            
            doc.close()
            return result
            
        except Exception as e:
            self.logger.error("Error analyzing page layout", 
                            error=str(e), pdf_path=pdf_path, page_number=page_number)
            return {}
    
    def _fallback_stamp_detection(self, pdf_path: str, page_number: int = 0) -> Optional[float]:
        """
        Fallback метод для детекции штампа без OpenCV
        Использует простую эвристику на основе размеров страницы
        """
        try:
            self.logger.debug("🔄 Using fallback stamp detection (no OpenCV)")
            
            doc = fitz.open(pdf_path)
            if page_number >= len(doc):
                self.logger.error("❌ Page number out of range in fallback", 
                                page_number=page_number, total_pages=len(doc))
                return None
                
            page = doc[page_number]
            page_rect = page.rect
            
            self.logger.debug("📄 Fallback page analysis", 
                            page_width=page_rect.width, 
                            page_height=page_rect.height,
                            aspect_ratio=page_rect.width/page_rect.height)
            
            # Простая эвристика: штамп обычно находится в нижней части страницы
            # Для landscape страниц - примерно на 10% от высоты страницы от низа
            if page_rect.width > page_rect.height:  # Landscape
                estimated_stamp_y = page_rect.height * 0.1  # 10% от высоты
                self.logger.info("✅ Fallback stamp detection (landscape)", 
                               estimated_y=estimated_stamp_y,
                               percentage=0.1,
                               method="heuristic")
                doc.close()
                return estimated_stamp_y
            else:
                self.logger.warning("⚠️ Fallback: page is not landscape", 
                                  page_width=page_rect.width, 
                                  page_height=page_rect.height)
            
            doc.close()
            return None
            
        except Exception as e:
            self.logger.error("❌ Error in fallback stamp detection", error=str(e))
            return None
    
    def _fallback_frame_detection(self, pdf_path: str, page_number: int = 0, frame_type: str = "right") -> Optional[float]:
        """
        Fallback метод для детекции рамки без OpenCV
        Использует простую эвристику на основе размеров страницы
        """
        try:
            doc = fitz.open(pdf_path)
            if page_number >= len(doc):
                return None
                
            page = doc[page_number]
            page_rect = page.rect
            
            if frame_type == "right":
                # Правая рамка обычно находится на 5% от ширины страницы от правого края
                estimated_frame_x = page_rect.width * 0.95  # 95% от ширины
                self.logger.info("Fallback right frame detection", estimated_x=estimated_frame_x)
                doc.close()
                return estimated_frame_x
            elif frame_type == "bottom":
                # Нижняя рамка обычно находится на 5% от высоты страницы от низа
                estimated_frame_y = page_rect.height * 0.05  # 5% от высоты
                self.logger.info("Fallback bottom frame detection", estimated_y=estimated_frame_y)
                doc.close()
                return estimated_frame_y
            
            doc.close()
            return None
            
        except Exception as e:
            self.logger.error("Error in fallback frame detection", error=str(e))
            return None
