"""
PDF analyzer for detecting stamp and frame positions
"""

import structlog
from typing import Dict, Any, Tuple, Optional, List
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
            stamp_detection_area_width_cm = 20.0  # Увеличили с 15 до 20 см для учета отступов и рамки
            stamp_detection_area_height_cm = 10.0  # Увеличили с 6 до 10 см для учета отступов и рамки
            stamp_width_pixels = int(stamp_detection_area_width_cm * 28.35 * 2.0)  # 20 см в пикселях
            stamp_height_pixels = int(stamp_detection_area_height_cm * 28.35 * 2.0)  # 10 см в пикселях
            
            # Определяем область поиска в правом нижнем углу
            right_start = max(0, img_array.shape[1] - stamp_width_pixels)
            bottom_start = max(0, img_array.shape[0] - stamp_height_pixels)
            
            # Извлекаем область поиска штампа
            stamp_region = img_array[bottom_start:, right_start:]
            
            # В данном месте, в целях отладки выделяем и сохраняем в файл область поиска штампа
            try:
                # Создаем PIL изображение из области поиска штампа
                stamp_pil = Image.fromarray(stamp_region)
                
                # Сохраняем в файл для отладки
                debug_filename = f"/app/tmp/stamp_region_debug_page_{page_number}.png"
                stamp_pil.save(debug_filename)
                
                self.logger.debug("💾 Saved stamp region for debugging", 
                                filename=debug_filename,
                                region_size=(stamp_region.shape[1], stamp_region.shape[0]),
                                region_size_cm=(round(stamp_region.shape[1] / (28.35 * 2.0), 2), 
                                              round(stamp_region.shape[0] / (28.35 * 2.0), 2)))
            except Exception as e:
                self.logger.warning("⚠️ Failed to save stamp region for debugging", error=str(e))

            self.logger.debug("🔍 Stamp region analysis", 
                            total_height=img_array.shape[0],
                            total_width=img_array.shape[1],
                            stamp_region_height=stamp_region.shape[0],
                            stamp_region_width=stamp_region.shape[1],
                            stamp_width_cm=stamp_detection_area_width_cm,
                            stamp_height_cm=stamp_detection_area_height_cm,
                            right_start=right_start,
                            bottom_start=bottom_start)
            
            # Ищем позицию правой рамки в области поиска штампа
            right_frame_x = self._find_right_frame_in_stamp_region(stamp_region, right_start, bottom_start)
            if right_frame_x is not None:
                self.logger.info("✅ Right frame found in stamp region", 
                               right_frame_x=right_frame_x,
                               right_frame_x_cm=round(right_frame_x / 28.35, 2))
            

            # Ищем позицию горизонтальной линии 18 см+ в области поиска штампа
            self.logger.info("🔍 Поиск горизонтальной линии 18 см+ в области поиска штампа")
            horizontal_line = self._find_horizontal_line_18cm_in_stamp_region(stamp_region, right_frame_x, right_start, bottom_start)
            if horizontal_line is not None:
                self.logger.info("✅ Horizontal line 18cm+ found in stamp region", 
                               horizontal_line_y=horizontal_line["y"],
                               horizontal_line_y_cm=round(horizontal_line["y"] / 28.35, 2))

            # Ищем позицию нижней рамки в области поиска штампа
            bottom_frame_y = self._find_bottom_frame_in_stamp_region(stamp_region, right_start, bottom_start)
            if bottom_frame_y is not None:
                self.logger.info("✅ Bottom frame found in stamp region", 
                               bottom_frame_y=bottom_frame_y,
                               bottom_frame_y_cm=round(bottom_frame_y / 28.35, 2))

            
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
    
    def detect_qr_position_in_stamp_region(self, pdf_path: str, page_number: int = 0) -> Optional[Dict[str, float]]:
        """
        Находит позицию для QR кода в области поиска штампа
        
        Алгоритм:
        1. В области поиска штампа находим правую рамку (крайнюю правую вертикальную линию)
        2. Ставим QR код слева от правой рамки
        3. Если правую рамку не нашли - fallback: ставим на 1 см от правого края листа
        4. Находим самую верхнюю горизонтальную линию длиной не менее 18 см, соприкасающуюся с правой рамкой
        5. Ставим QR над этой линией
        6. Если fallback - ищем нижнюю горизонтальную линию и ставим QR над ней
        7. Если fallback - ставим QR на 1 см выше нижнего края листа
        
        Args:
            pdf_path: Путь к PDF файлу
            page_number: Номер страницы (начиная с 0)
            
        Returns:
            Словарь с координатами позиции QR кода или None
            {"x": float, "y": float, "width": float, "height": float}
        """
        if not CV_AVAILABLE:
            self.logger.warning("OpenCV not available, using fallback QR positioning")
            return self._fallback_qr_position_in_stamp_region(pdf_path, page_number)
            
        try:
            self.logger.debug("🔍 Starting QR position detection in stamp region", 
                            pdf_path=pdf_path, page_number=page_number)
            
            # Открываем PDF
            doc = fitz.open(pdf_path)
            if page_number >= len(doc):
                self.logger.error("❌ Page number out of range", 
                                page_number=page_number, total_pages=len(doc))
                return None
                
            page = doc[page_number]
            page_rect = page.rect
            page_width = page_rect.width
            page_height = page_rect.height
            
            # Конвертируем страницу в изображение
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            pil_image = Image.open(io.BytesIO(img_data))
            img_array = np.array(pil_image.convert('L'))
            
            # Определяем область поиска штампа (правый нижний угол)
            stamp_width_cm = 20.0
            stamp_height_cm = 10.0
            stamp_width_pixels = int(stamp_width_cm * 28.35 * 2.0)
            stamp_height_pixels = int(stamp_height_cm * 28.35 * 2.0)
            
            right_start = max(0, img_array.shape[1] - stamp_width_pixels)
            bottom_start = max(0, img_array.shape[0] - stamp_height_pixels)
            
            # Извлекаем область поиска штампа
            stamp_region = img_array[bottom_start:, right_start:]
            
            self.logger.debug("🔍 Analyzing stamp region for QR positioning", 
                            region_size=(stamp_region.shape[1], stamp_region.shape[0]),
                            region_size_cm=(round(stamp_region.shape[1] / (28.35 * 2.0), 2), 
                                          round(stamp_region.shape[0] / (28.35 * 2.0), 2)))
            
            # Размер QR кода
            qr_size_cm = 3.5
            qr_size_points = qr_size_cm * 28.35
            margin_cm = 0.5
            margin_points = margin_cm * 28.35
            
            # Шаг 1: Находим правую рамку в области поиска штампа
            right_frame_x = self._find_right_frame_in_stamp_region(stamp_region, right_start, bottom_start)
            
            if right_frame_x is not None:
                self.logger.info("✅ Right frame found in stamp region", 
                               right_frame_x=right_frame_x,
                               right_frame_x_cm=round(right_frame_x / 28.35, 2))
                
                # Шаг 2: Находим горизонтальную линию длиной не менее 18 см, соприкасающуюся с правой рамкой
                horizontal_line = self._find_horizontal_line_18cm_in_stamp_region(
                    stamp_region, right_frame_x, right_start, bottom_start)
                
                if horizontal_line:
                    self.logger.info("✅ Horizontal line 18cm+ found in stamp region", 
                                   line_y=horizontal_line["y"],
                                   line_length_cm=horizontal_line["length_cm"])
                    
                    # Позиционируем QR код слева от правой рамки и над горизонтальной линией
                    x_position = right_frame_x - qr_size_points - margin_points
                    y_position = horizontal_line["y"] - qr_size_points - margin_points
                    
                    # Проверяем, что QR код помещается в области
                    if x_position >= right_start and y_position >= bottom_start:
                        result = {
                            "x": x_position,
                            "y": y_position,
                            "width": qr_size_points,
                            "height": qr_size_points
                        }
                        
                        self.logger.info("✅ QR position calculated using right frame and horizontal line", 
                                       x=result["x"], y=result["y"],
                                       x_cm=round(result["x"] / 28.35, 2),
                                       y_cm=round(result["y"] / 28.35, 2))
                        
                        doc.close()
                        return result
                
                # Fallback: ищем нижнюю горизонтальную линию
                self.logger.warning("⚠️ No suitable horizontal line found, trying bottom line fallback")
                bottom_line = self._find_bottom_horizontal_line_in_stamp_region(
                    stamp_region, right_frame_x, right_start, bottom_start)
                
                if bottom_line:
                    self.logger.info("✅ Bottom horizontal line found in stamp region", 
                                   line_y=bottom_line["y"],
                                   line_length_cm=bottom_line["length_cm"])
                    
                    # Позиционируем QR код слева от правой рамки и над нижней линией
                    x_position = right_frame_x - qr_size_points - margin_points
                    y_position = bottom_line["y"] - qr_size_points - margin_points
                    
                    if x_position >= right_start and y_position >= bottom_start:
                        result = {
                            "x": x_position,
                            "y": y_position,
                            "width": qr_size_points,
                            "height": qr_size_points
                        }
                        
                        self.logger.info("✅ QR position calculated using right frame and bottom line", 
                                       x=result["x"], y=result["y"],
                                       x_cm=round(result["x"] / 28.35, 2),
                                       y_cm=round(result["y"] / 28.35, 2))
                        
                        doc.close()
                        return result
                
                # Fallback: ставим QR на 1 см выше нижнего края листа
                self.logger.warning("⚠️ No horizontal lines found, using bottom edge fallback")
                x_position = right_frame_x - qr_size_points - margin_points
                y_position = page_height - qr_size_points - (1.0 * 28.35)  # 1 см от нижнего края
                
                result = {
                    "x": x_position,
                    "y": y_position,
                    "width": qr_size_points,
                    "height": qr_size_points
                }
                
                self.logger.info("✅ QR position calculated using right frame and bottom edge fallback", 
                               x=result["x"], y=result["y"],
                               x_cm=round(result["x"] / 28.35, 2),
                               y_cm=round(result["y"] / 28.35, 2))
                
                doc.close()
                return result
            
            else:
                # Fallback: правую рамку не нашли, ставим на 1 см от правого края листа
                self.logger.warning("⚠️ Right frame not found in stamp region, using right edge fallback")
                x_position = page_width - qr_size_points - (1.0 * 28.35)  # 1 см от правого края
                y_position = page_height - qr_size_points - (1.0 * 28.35)  # 1 см от нижнего края
                
                result = {
                    "x": x_position,
                    "y": y_position,
                    "width": qr_size_points,
                    "height": qr_size_points
                }
                
                self.logger.info("✅ QR position calculated using right edge fallback", 
                               x=result["x"], y=result["y"],
                               x_cm=round(result["x"] / 28.35, 2),
                               y_cm=round(result["y"] / 28.35, 2))
                
                doc.close()
                return result
                
        except Exception as e:
            self.logger.error("Error detecting QR position in stamp region", 
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
                "bottom_frame_edge": None,
                "horizontal_line_18cm": None,
                "free_space_3_5cm": None
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
            
            # Определяем горизонтальную линию длиной не менее 18 см
            horizontal_line = self.detect_horizontal_line_18cm(pdf_path, page_number)
            result["horizontal_line_18cm"] = horizontal_line
            
            # Ищем свободное место 3.5x3.5 см в нижнем левом углу
            free_space = self.detect_free_space_3_5cm(pdf_path, page_number)
            result["free_space_3_5cm"] = free_space
            
            self.logger.info("Page layout analysis completed", 
                           page_number=page_number,
                           is_landscape=is_landscape,
                           stamp_top_edge=stamp_top,
                           right_frame_edge=right_frame,
                           horizontal_line_18cm=horizontal_line,
                           free_space_3_5cm=free_space)
            
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
    
    def detect_horizontal_line_18cm(self, pdf_path: str, page_number: int = 0) -> Optional[Dict[str, float]]:
        """
        Определяет верхнюю горизонтальную линию длиной не менее 15 см в верхней части листа
        
        Args:
            pdf_path: Путь к PDF файлу
            page_number: Номер страницы (начиная с 0)
            
        Returns:
            Словарь с информацией о найденной горизонтальной линии или None
            {"start_x": float, "end_x": float, "y": float, "length_cm": float}
        """
        if not CV_AVAILABLE:
            self.logger.warning("OpenCV not available, using fallback horizontal line detection")
            return self._fallback_horizontal_line_detection(pdf_path, page_number)
            
        try:
            self.logger.debug("🔍 Detecting horizontal line 18cm+ in top area", 
                            pdf_path=pdf_path, page_number=page_number)
            
            # Открываем PDF с помощью PyMuPDF
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
            
            # Конвертируем страницу в изображение
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Конвертируем в PIL Image
            pil_image = Image.open(io.BytesIO(img_data))
            img_array = np.array(pil_image.convert('L'))
            
            # Ищем горизонтальные линии в верхней части страницы (верхние 30%)
            top_region_height = int(page_height * 0.3)
            top_region = img_array[:top_region_height, :]
            
            self.logger.debug("📊 Top region analysis", 
                            total_height=img_array.shape[0],
                            top_region_height=top_region.shape[0],
                            top_region_width=top_region.shape[1])
            
            # Применяем детекцию краев
            edges = cv2.Canny(top_region, 30, 100)
            
            # Ищем горизонтальные линии
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 1))
            horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
            
            # Находим контуры горизонтальных линий
            contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Минимальная длина линии: 15 см в пикселях (снижено с 18 см для лучшего обнаружения)
            min_length_pixels = int(15.0 * 28.35 * 2.0)  # 15 см в пикселях с масштабом 2.0
            
            self.logger.debug("📏 Line length requirements", 
                            min_length_cm=15.0,
                            min_length_pixels=min_length_pixels)
            
            # Ищем самую верхнюю горизонтальную линию длиной не менее 15 см
            valid_lines = []
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Проверяем, что это горизонтальная линия достаточной длины
                if w >= min_length_pixels and h <= 5:  # Горизонтальная линия не должна быть слишком толстой
                    line_length_cm = w / (28.35 * 2.0)  # Конвертируем в см
                    
                    valid_lines.append({
                        "start_x": x,
                        "end_x": x + w,
                        "y": y,
                        "length_cm": line_length_cm
                    })
                    
                    self.logger.debug("🎯 Found candidate horizontal line in top area", 
                                    bbox=(x, y, w, h),
                                    length_cm=line_length_cm)
            
            if not valid_lines:
                self.logger.warning("❌ No horizontal line 15cm+ found in top area")
                doc.close()
                return None
            
            # Сортируем линии по Y-позиции (от верха к низу) и выбираем самую верхнюю
            valid_lines.sort(key=lambda line: line["y"])  # Сортируем от верха к низу
            
            self.logger.debug("📊 Found horizontal lines in top area", 
                            total_lines=len(valid_lines),
                            lines_info=[f"Y={line['y']}, length={line['length_cm']:.1f}cm" 
                                       for line in valid_lines[:5]])  # Показываем первые 5
            
            # Выбираем самую верхнюю линию
            best_line = valid_lines[0]
            self.logger.info("✅ Selected topmost horizontal line", 
                           y_position=best_line["y"],
                           length_cm=best_line["length_cm"],
                           total_candidates=len(valid_lines))
            
            # Конвертируем координаты обратно в PDF точки
            # best_line координаты относительно top_region
            actual_y = best_line["y"]
            
            # Конвертируем из пикселей изображения в PDF точки
            scale_factor = 2.0
            line_info = {
                "start_x": best_line["start_x"] / scale_factor,
                "end_x": best_line["end_x"] / scale_factor,
                "y": (img_array.shape[0] - actual_y) / scale_factor,
                "length_cm": best_line["length_cm"]
            }
            
            self.logger.info("✅ Top horizontal line 15cm+ detected", 
                           start_x=line_info["start_x"],
                           end_x=line_info["end_x"],
                           y=line_info["y"],
                           length_cm=line_info["length_cm"])
            
            doc.close()
            return line_info
            
        except Exception as e:
            self.logger.error("❌ Error detecting top horizontal line 15cm+", 
                            error=str(e), pdf_path=pdf_path, page_number=page_number)
            return None
    
    def detect_free_space_3_5cm(self, pdf_path: str, page_number: int = 0) -> Optional[Dict[str, float]]:
        """
        Ищет свободное место размером 3.5x3.5 см для QR кода
        
        Новый алгоритм:
        1. Сначала пытается найти позицию в области поиска штампа (правый нижний угол)
        2. Если не удается, использует старый алгоритм поиска в верхней части листа
        
        Args:
            pdf_path: Путь к PDF файлу
            page_number: Номер страницы (начиная с 0)
            
        Returns:
            Словарь с координатами свободного места или None
            {"x": float, "y": float, "width": float, "height": float}
        """
        try:
            self.logger.debug("🔍 Searching for free space 3.5x3.5cm with new algorithm", 
                            pdf_path=pdf_path, page_number=page_number)
            
            # Шаг 1: Пытаемся найти позицию в области поиска штампа
            self.logger.debug("🔍 Step 1: Trying to find QR position in stamp region")
            stamp_region_position = self.detect_qr_position_in_stamp_region(pdf_path, page_number)
            
            if stamp_region_position:
                self.logger.info("✅ QR position found in stamp region", 
                               x=stamp_region_position["x"], y=stamp_region_position["y"],
                               x_cm=round(stamp_region_position["x"] / 28.35, 2),
                               y_cm=round(stamp_region_position["y"] / 28.35, 2))
                return stamp_region_position
            
            # Шаг 2: Fallback к старому алгоритму поиска в верхней части листа
            self.logger.warning("⚠️ No position found in stamp region, falling back to top area algorithm")
            return self._detect_free_space_3_5cm_top_area(pdf_path, page_number)
            
        except Exception as e:
            self.logger.error("❌ Error detecting free space 3.5x3.5cm", 
                            error=str(e), pdf_path=pdf_path, page_number=page_number)
            return None
    
    def _detect_free_space_3_5cm_top_area(self, pdf_path: str, page_number: int = 0) -> Optional[Dict[str, float]]:
        """
        Старый алгоритм поиска свободного места в верхней части листа
        (переименованный оригинальный метод detect_free_space_3_5cm)
        
        Args:
            pdf_path: Путь к PDF файлу
            page_number: Номер страницы (начиная с 0)
            
        Returns:
            Словарь с координатами свободного места или None
            {"x": float, "y": float, "width": float, "height": float}
        """
        try:
            self.logger.debug("🔍 Searching for free space 3.5x3.5cm in top area with alternative positioning", 
                            pdf_path=pdf_path, page_number=page_number)
            
            # Получаем информацию о правой рамке
            right_frame = self.detect_right_frame_edge(pdf_path, page_number)
            
            # Получаем все горизонтальные линии
            horizontal_lines = self._find_all_horizontal_lines(pdf_path, page_number)
            
            if not horizontal_lines:
                self.logger.warning("❌ No horizontal lines 15cm+ found, cannot determine QR position")
                return None
            
            # Размер QR кода: 3.5 см x 3.5 см
            qr_size_cm = 3.5
            qr_size_points = qr_size_cm * 28.35  # 99.225 точек
            
            # Отступы от краев
            margin_cm = 0.5  # 0.5 см отступ
            margin_points = margin_cm * 28.35
            
            # Получаем размеры страницы
            doc = fitz.open(pdf_path)
            page = doc[page_number]
            page_rect = page.rect
            page_width = page_rect.width
            page_height = page_rect.height
            doc.close()
            
            # Пробуем каждую горизонтальную линию, начиная с самой верхней
            for i, horizontal_line in enumerate(horizontal_lines):
                self.logger.debug("🔍 Trying horizontal line {} of {}".format(i + 1, len(horizontal_lines)),
                                line_y=horizontal_line["y"],
                                line_length_cm=horizontal_line["length_cm"])
                
                # Вычисляем позицию QR кода для этой линии
                x_position, y_position = self._calculate_qr_position_for_line(
                    horizontal_line, right_frame, qr_size_points, margin_points, 
                    page_width, page_height
                )
                
                self.logger.debug("📍 Calculated QR position for line {}: ({}, {})".format(i + 1, x_position, y_position))
                
                # Проверяем, что область действительно пустая
                is_empty = self._is_area_empty(pdf_path, page_number, x_position, y_position, qr_size_points, qr_size_points)
                
                if is_empty:
                    result = {
                        "x": x_position,
                        "y": y_position,
                        "width": qr_size_points,
                        "height": qr_size_points
                    }
                    
                    self.logger.info("✅ Free space 3.5x3.5cm found and verified as empty using line {} of {}".format(i + 1, len(horizontal_lines)), 
                                   line_y=horizontal_line["y"],
                                   line_length_cm=horizontal_line["length_cm"],
                                   x=result["x"],
                                   y=result["y"],
                                   width=result["width"],
                                   height=result["height"],
                                   x_cm=round(result["x"] / 28.35, 2),
                                   y_cm=round(result["y"] / 28.35, 2))
                    
                    return result
                else:
                    self.logger.warning("❌ Area for line {} is not empty, trying next line".format(i + 1),
                                      line_y=horizontal_line["y"],
                                      x_position=x_position,
                                      y_position=y_position,
                                      x_cm=round(x_position / 28.35, 2),
                                      y_cm=round(y_position / 28.35, 2))
            
            # Если ни одна линия не подошла, возвращаем None (будет использован fallback)
            self.logger.warning("❌ No empty space found for any horizontal line, will use fallback algorithm")
            return None
            
        except Exception as e:
            self.logger.error("❌ Error detecting free space 3.5x3.5cm in top area", 
                            error=str(e), pdf_path=pdf_path, page_number=page_number)
            return None
    
    def _find_all_horizontal_lines(self, pdf_path: str, page_number: int = 0) -> List[Dict[str, float]]:
        """
        Находит все горизонтальные линии длиной не менее 15 см в верхней части страницы
        
        Args:
            pdf_path: Путь к PDF файлу
            page_number: Номер страницы (начиная с 0)
            
        Returns:
            Список словарей с информацией о найденных горизонтальных линиях
            [{"start_x": float, "end_x": float, "y": float, "length_cm": float}, ...]
        """
        if not CV_AVAILABLE:
            self.logger.warning("OpenCV not available, using fallback horizontal line detection")
            fallback_line = self._fallback_horizontal_line_detection(pdf_path, page_number)
            return [fallback_line] if fallback_line else []
            
        try:
            self.logger.debug("🔍 Finding all horizontal lines 15cm+ in top area", 
                            pdf_path=pdf_path, page_number=page_number)
            
            # Открываем PDF с помощью PyMuPDF
            doc = fitz.open(pdf_path)
            if page_number >= len(doc):
                self.logger.error("❌ Page number out of range", 
                                page_number=page_number, total_pages=len(doc))
                return []
                
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
            
            # Ищем горизонтальные линии в верхней части страницы (верхние 30%)
            top_region_height = int(page_height * 0.3)
            top_region = img_array[:top_region_height, :]
            
            self.logger.debug("📊 Top region analysis", 
                            total_height=img_array.shape[0],
                            top_region_height=top_region.shape[0],
                            top_region_width=top_region.shape[1])
            
            # Применяем детекцию краев
            edges = cv2.Canny(top_region, 30, 100)
            
            # Ищем горизонтальные линии
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 1))
            horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
            
            # Находим контуры горизонтальных линий
            contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Минимальная длина линии: 15 см в пикселях
            min_length_pixels = int(15.0 * 28.35 * 2.0)  # 15 см в пикселях с масштабом 2.0
            
            self.logger.debug("📏 Line length requirements", 
                            min_length_cm=15.0,
                            min_length_pixels=min_length_pixels)
            
            # Ищем все горизонтальные линии длиной не менее 15 см
            valid_lines = []
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Проверяем, что это горизонтальная линия достаточной длины
                if w >= min_length_pixels and h <= 5:  # Горизонтальная линия не должна быть слишком толстой
                    line_length_cm = w / (28.35 * 2.0)  # Конвертируем в см
                    
                    valid_lines.append({
                        "start_x": x,
                        "end_x": x + w,
                        "y": y,
                        "length_cm": line_length_cm
                    })
                    
                    self.logger.debug("🎯 Found candidate horizontal line in top area", 
                                    bbox=(x, y, w, h),
                                    length_cm=line_length_cm)
            
            if not valid_lines:
                self.logger.warning("❌ No horizontal line 15cm+ found in top area")
                doc.close()
                return []
            
            # Сортируем линии по Y-позиции (от верха к низу)
            valid_lines.sort(key=lambda line: line["y"])
            
            self.logger.debug("📊 Found horizontal lines in top area", 
                            total_lines=len(valid_lines),
                            lines_info=[f"Y={line['y']}, length={line['length_cm']:.1f}cm" 
                                       for line in valid_lines])
            
            # Конвертируем координаты обратно в PDF точки
            scale_factor = 2.0
            result_lines = []
            
            for line in valid_lines:
                line_info = {
                    "start_x": line["start_x"] / scale_factor,
                    "end_x": line["end_x"] / scale_factor,
                    "y": (img_array.shape[0] - line["y"]) / scale_factor,
                    "length_cm": line["length_cm"]
                }
                result_lines.append(line_info)
            
            self.logger.info("✅ Found {} horizontal lines 15cm+ in top area".format(len(result_lines)))
            
            doc.close()
            return result_lines
            
        except Exception as e:
            self.logger.error("❌ Error finding all horizontal lines 15cm+", 
                            error=str(e), pdf_path=pdf_path, page_number=page_number)
            return []
    
    def _is_area_empty(self, pdf_path: str, page_number: int, x: float, y: float, width: float, height: float) -> bool:
        """
        Проверяет, является ли указанная область изображения пустой (без значимых элементов)
        
        Args:
            pdf_path: Путь к PDF файлу
            page_number: Номер страницы (начиная с 0)
            x, y: Координаты левого верхнего угла области в PDF точках
            width, height: Размеры области в PDF точках
            
        Returns:
            True если область пустая, False если содержит элементы
        """
        if not CV_AVAILABLE:
            self.logger.warning("OpenCV not available, assuming area is empty")
            return True
            
        try:
            self.logger.debug("🔍 Checking if area is empty", 
                            x=x, y=y, width=width, height=height,
                            x_cm=round(x / 28.35, 2), y_cm=round(y / 28.35, 2),
                            width_cm=round(width / 28.35, 2), height_cm=round(height / 28.35, 2))
            
            # Открываем PDF
            doc = fitz.open(pdf_path)
            if page_number >= len(doc):
                self.logger.error("❌ Page number out of range", 
                                page_number=page_number, total_pages=len(doc))
                return False
                
            page = doc[page_number]
            
            # Конвертируем страницу в изображение
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Конвертируем в PIL Image
            pil_image = Image.open(io.BytesIO(img_data))
            img_array = np.array(pil_image.convert('L'))
            
            # Конвертируем координаты из PDF точек в пиксели изображения
            scale_factor = 2.0
            x_pixels = int(x * scale_factor)
            y_pixels = int(y * scale_factor)
            width_pixels = int(width * scale_factor)
            height_pixels = int(height * scale_factor)
            
            # Проверяем границы
            if (x_pixels < 0 or y_pixels < 0 or 
                x_pixels + width_pixels > img_array.shape[1] or 
                y_pixels + height_pixels > img_array.shape[0]):
                self.logger.warning("⚠️ Area extends beyond image boundaries", 
                                  x_pixels=x_pixels, y_pixels=y_pixels,
                                  width_pixels=width_pixels, height_pixels=height_pixels,
                                  img_width=img_array.shape[1], img_height=img_array.shape[0])
                return False
            
            # Извлекаем область для анализа
            area = img_array[y_pixels:y_pixels + height_pixels, 
                           x_pixels:x_pixels + width_pixels]
            
            # Анализируем область на наличие элементов
            # Вычисляем статистики яркости
            mean_brightness = np.mean(area)
            std_brightness = np.std(area)
            
            # Область считается пустой, если:
            # 1. Средняя яркость близка к белому (высокие значения)
            # 2. Низкое стандартное отклонение (мало вариации)
            # 3. Мало краев (отсутствие значимых элементов)
            is_bright = mean_brightness > 200  # Близко к белому
            is_uniform = std_brightness < 100  # Мало вариации (смягчено до 100)
            
            # Дополнительная проверка: ищем края в области
            edges = cv2.Canny(area, 50, 150)
            edge_pixels = np.sum(edges > 0)
            total_pixels = area.shape[0] * area.shape[1]
            edge_ratio = edge_pixels / total_pixels
            
            # Область считается пустой, если мало краев
            has_few_edges = edge_ratio < 0.05  # Менее 5% пикселей являются краями
            
            # Дополнительная проверка: если область очень яркая, то даже при наличии краев считаем её пустой
            is_very_bright = mean_brightness > 240  # Очень близко к белому
            
            is_empty = (is_bright and is_uniform and has_few_edges) or is_very_bright
            
            self.logger.debug("📊 Area analysis results", 
                            mean_brightness=round(mean_brightness, 1),
                            std_brightness=round(std_brightness, 1),
                            edge_pixels=edge_pixels,
                            total_pixels=total_pixels,
                            edge_ratio=round(edge_ratio, 3),
                            is_bright=is_bright,
                            is_uniform=is_uniform,
                            has_few_edges=has_few_edges,
                            is_very_bright=is_very_bright,
                            is_empty=is_empty)
            
            doc.close()
            return is_empty
            
        except Exception as e:
            self.logger.error("❌ Error checking if area is empty", 
                            error=str(e), pdf_path=pdf_path, page_number=page_number)
            return True  # В случае ошибки считаем область пустой
    
    def _calculate_qr_position_for_line(self, horizontal_line: Dict[str, float], right_frame: Optional[float], 
                                      qr_size_points: float, margin_points: float, 
                                      page_width: float, page_height: float) -> tuple[float, float]:
        """
        Вычисляет позицию QR кода для заданной горизонтальной линии
        
        Args:
            horizontal_line: Информация о горизонтальной линии
            right_frame: Позиция правой рамки (если есть)
            qr_size_points: Размер QR кода в точках
            margin_points: Отступ в точках
            page_width: Ширина страницы в точках
            page_height: Высота страницы в точках
            
        Returns:
            Tuple (x_position, y_position) в точках
        """
        # Y-позиция: ниже горизонтальной линии с отступом
        y_position = horizontal_line["y"] - qr_size_points - margin_points
        
        # X-позиция: если есть правая рамка, используем её, иначе от левого края
        if right_frame:
            # Позиционируем слева от правой рамки с отступом
            x_position = right_frame - qr_size_points - margin_points
            
            # Проверяем, что QR код не выходит за левый край
            min_x = margin_points
            if x_position < min_x:
                x_position = min_x
        else:
            # Fallback: позиционируем в левом верхнем углу
            x_position = margin_points
        
        # Проверяем, что QR код помещается в области горизонтальной линии
        if x_position + qr_size_points > horizontal_line["end_x"]:
            # Сдвигаем влево, чтобы поместиться в области линии
            x_position = horizontal_line["end_x"] - qr_size_points - margin_points
        
        # Проверяем границы страницы
        if x_position < margin_points:
            x_position = margin_points
        if x_position + qr_size_points > page_width - margin_points:
            x_position = page_width - qr_size_points - margin_points
        if y_position < margin_points:
            y_position = margin_points
        if y_position + qr_size_points > page_height - margin_points:
            y_position = page_height - qr_size_points - margin_points
        
        return x_position, y_position
    
    def _fallback_horizontal_line_detection(self, pdf_path: str, page_number: int = 0) -> Optional[Dict[str, float]]:
        """
        Fallback метод для детекции горизонтальной линии без OpenCV
        """
        try:
            self.logger.debug("🔄 Using fallback horizontal line detection (no OpenCV)")
            
            doc = fitz.open(pdf_path)
            if page_number >= len(doc):
                return None
                
            page = doc[page_number]
            page_rect = page.rect
            
            # Простая эвристика: предполагаем горизонтальную линию в верхней части
            # Примерно на 10% от высоты страницы от верха
            estimated_y = page_rect.height * 0.9
            estimated_start_x = page_rect.width * 0.1  # 10% от левого края
            estimated_end_x = page_rect.width * 0.9    # 90% от левого края
            estimated_length_cm = (estimated_end_x - estimated_start_x) / 28.35
            
            result = {
                "start_x": estimated_start_x,
                "end_x": estimated_end_x,
                "y": estimated_y,
                "length_cm": estimated_length_cm
            }
            
            self.logger.info("✅ Fallback horizontal line detection (top area)", 
                           start_x=result["start_x"],
                           end_x=result["end_x"],
                           y=result["y"],
                           length_cm=result["length_cm"],
                           method="heuristic_top")
            
            doc.close()
            return result
            
        except Exception as e:
            self.logger.error("❌ Error in fallback horizontal line detection", error=str(e))
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
    
    def _find_right_frame_in_stamp_region(self, stamp_region: np.ndarray, right_start: int, bottom_start: int) -> Optional[float]:
        """
        Находит правую рамку (крайнюю правую вертикальную линию) в области поиска штампа
        
        Args:
            stamp_region: Область поиска штампа как numpy array
            right_start: Начальная X координата области поиска в пикселях
            bottom_start: Начальная Y координата области поиска в пикселях
            
        Returns:
            X координата правой рамки в PDF точках или None
        """
        try:
            # Применяем детекцию краев для поиска вертикальных линий
            edges = cv2.Canny(stamp_region, 30, 100)
            
            # Ищем вертикальные линии с помощью HoughLinesP
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                                  minLineLength=100, maxLineGap=10)
            
            if lines is None:
                self.logger.debug("❌ No lines found in stamp region")
                return None
            
            # Фильтруем вертикальные линии (угол близкий к 90 градусам)
            vertical_lines = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if x1 == x2:  # Строго вертикальная линия
                    vertical_lines.append(x1)
                else:
                    # Проверяем угол наклона
                    angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                    if abs(angle - 90) < 10 or abs(angle + 90) < 10:  # Вертикальная линия
                        vertical_lines.append((x1 + x2) // 2)
            
            if not vertical_lines:
                self.logger.debug("❌ No vertical lines found in stamp region")
                return None
            
            # Находим крайнюю правую вертикальную линию
            rightmost_x = max(vertical_lines)
            
            # Конвертируем в PDF координаты
            right_frame_x_points = (right_start + rightmost_x) / 2.0  # Масштаб 2.0
            
            self.logger.debug("✅ Right frame found in stamp region", 
                            rightmost_x_pixels=rightmost_x,
                            right_frame_x_points=right_frame_x_points,
                            right_frame_x_cm=round(right_frame_x_points / 28.35, 2))
            
            return right_frame_x_points
            
        except Exception as e:
            self.logger.error("Error finding right frame in stamp region", error=str(e))
            return None
    
    def _find_horizontal_line_18cm_in_stamp_region(self, stamp_region: np.ndarray, right_frame_x: float, 
                                                 right_start: int, bottom_start: int) -> Optional[Dict[str, float]]:
        """
        Находит самую верхнюю горизонтальную линию длиной не менее 18 см, соприкасающуюся с правой рамкой
        
        Args:
            stamp_region: Область поиска штампа как numpy array
            right_frame_x: X координата правой рамки в PDF точках
            right_start: Начальная X координата области поиска в пикселях
            bottom_start: Начальная Y координата области поиска в пикселях
            
        Returns:
            Словарь с информацией о горизонтальной линии или None
            {"y": float, "length_cm": float}
        """
        try:
            # Применяем детекцию краев
            edges = cv2.Canny(stamp_region, 30, 100)
            
            # Ищем горизонтальные линии
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                                  minLineLength=100, maxLineGap=10)
            
            if lines is None:
                self.logger.debug("❌ No lines found for horizontal line detection")
                return None
            
            # Минимальная длина линии в пикселях (18 см)
            min_length_pixels = int(18.0 * 28.35 * 2.0)  # 18 см в пикселях
            
            # Конвертируем правую рамку в пиксели области поиска
            right_frame_x_pixels = int((right_frame_x - right_start) * 2.0)
            
            # Фильтруем горизонтальные линии
            horizontal_lines = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if y1 == y2:  # Строго горизонтальная линия
                    length = abs(x2 - x1)
                    if length >= min_length_pixels:
                        # Проверяем, соприкасается ли линия с правой рамкой
                        if (x1 <= right_frame_x_pixels <= x2) or (x2 <= right_frame_x_pixels <= x1):
                            horizontal_lines.append((y1, length))
                else:
                    # Проверяем угол наклона
                    angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                    if abs(angle) < 10 or abs(angle - 180) < 10:  # Горизонтальная линия
                        length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                        if length >= min_length_pixels:
                            # Проверяем, соприкасается ли линия с правой рамкой
                            if (x1 <= right_frame_x_pixels <= x2) or (x2 <= right_frame_x_pixels <= x1):
                                horizontal_lines.append(((y1 + y2) // 2, length))
            
            if not horizontal_lines:
                self.logger.debug("❌ No horizontal lines 18cm+ found in stamp region")
                return None
            
            # Находим самую верхнюю линию (минимальная Y координата)
            top_line = min(horizontal_lines, key=lambda x: x[0])
            y_pixels, length_pixels = top_line
            
            # Конвертируем в PDF координаты
            y_points = (bottom_start + y_pixels) / 2.0  # Масштаб 2.0
            length_cm = length_pixels / (28.35 * 2.0)
            
            result = {
                "y": y_points,
                "length_cm": length_cm
            }
            
            self.logger.debug("✅ Top horizontal line 18cm+ found in stamp region", 
                            y_pixels=y_pixels, y_points=y_points,
                            length_pixels=length_pixels, length_cm=length_cm)
            
            return result
            
        except Exception as e:
            self.logger.error("Error finding horizontal line in stamp region", error=str(e))
            return None
    
    def _find_bottom_horizontal_line_in_stamp_region(self, stamp_region: np.ndarray, right_frame_x: float, 
                                                   right_start: int, bottom_start: int) -> Optional[Dict[str, float]]:
        """
        Находит нижнюю горизонтальную линию в области поиска штампа
        
        Args:
            stamp_region: Область поиска штампа как numpy array
            right_frame_x: X координата правой рамки в PDF точках
            right_start: Начальная X координата области поиска в пикселях
            bottom_start: Начальная Y координата области поиска в пикселях
            
        Returns:
            Словарь с информацией о горизонтальной линии или None
            {"y": float, "length_cm": float}
        """
        try:
            # Применяем детекцию краев
            edges = cv2.Canny(stamp_region, 30, 100)
            
            # Ищем горизонтальные линии
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                                  minLineLength=50, maxLineGap=10)  # Меньше требований к длине
            
            if lines is None:
                self.logger.debug("❌ No lines found for bottom horizontal line detection")
                return None
            
            # Конвертируем правую рамку в пиксели области поиска
            right_frame_x_pixels = int((right_frame_x - right_start) * 2.0)
            
            # Фильтруем горизонтальные линии
            horizontal_lines = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if y1 == y2:  # Строго горизонтальная линия
                    length = abs(x2 - x1)
                    if length >= 50:  # Минимальная длина
                        # Проверяем, соприкасается ли линия с правой рамкой
                        if (x1 <= right_frame_x_pixels <= x2) or (x2 <= right_frame_x_pixels <= x1):
                            horizontal_lines.append((y1, length))
                else:
                    # Проверяем угол наклона
                    angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                    if abs(angle) < 10 or abs(angle - 180) < 10:  # Горизонтальная линия
                        length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                        if length >= 50:  # Минимальная длина
                            # Проверяем, соприкасается ли линия с правой рамкой
                            if (x1 <= right_frame_x_pixels <= x2) or (x2 <= right_frame_x_pixels <= x1):
                                horizontal_lines.append(((y1 + y2) // 2, length))
            
            if not horizontal_lines:
                self.logger.debug("❌ No horizontal lines found in stamp region")
                return None
            
            # Находим самую нижнюю линию (максимальная Y координата)
            bottom_line = max(horizontal_lines, key=lambda x: x[0])
            y_pixels, length_pixels = bottom_line
            
            # Конвертируем в PDF координаты
            y_points = (bottom_start + y_pixels) / 2.0  # Масштаб 2.0
            length_cm = length_pixels / (28.35 * 2.0)
            
            result = {
                "y": y_points,
                "length_cm": length_cm
            }
            
            self.logger.debug("✅ Bottom horizontal line found in stamp region", 
                            y_pixels=y_pixels, y_points=y_points,
                            length_pixels=length_pixels, length_cm=length_cm)
            
            return result
            
        except Exception as e:
            self.logger.error("Error finding bottom horizontal line in stamp region", error=str(e))
            return None
    
    def _find_bottom_frame_in_stamp_region(self, stamp_region: np.ndarray, right_start: int, bottom_start: int) -> Optional[float]:
        """
        Находит нижнюю рамку в области поиска штампа
        
        Args:
            stamp_region: Область поиска штампа как numpy array
            right_start: Начальная X координата области поиска в пикселях
            bottom_start: Начальная Y координата области поиска в пикселях
            
        Returns:
            Y координата нижней рамки в PDF точках или None
        """
        try:
            # Применяем детекцию краев для поиска горизонтальных линий
            edges = cv2.Canny(stamp_region, 30, 100)
            
            # Ищем горизонтальные линии
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                                  minLineLength=100, maxLineGap=10)
            
            if lines is None:
                return None
            
            # Фильтруем горизонтальные линии
            horizontal_lines = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if y1 == y2:  # Строго горизонтальная линия
                    horizontal_lines.append(y1)
                else:
                    # Проверяем угол наклона
                    angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                    if abs(angle) < 10 or abs(angle - 180) < 10:  # Горизонтальная линия
                        horizontal_lines.append((y1 + y2) // 2)
            
            if not horizontal_lines:
                return None
            
            # Находим самую нижнюю горизонтальную линию
            bottommost_y = max(horizontal_lines)
            
            # Конвертируем в PDF координаты
            bottom_frame_y_points = (bottom_start + bottommost_y) / 2.0  # Масштаб 2.0
            
            return bottom_frame_y_points
            
        except Exception as e:
            self.logger.error("Error finding bottom frame in stamp region", error=str(e))
            return None

    def _fallback_qr_position_in_stamp_region(self, pdf_path: str, page_number: int = 0) -> Optional[Dict[str, float]]:
        """
        Fallback метод для позиционирования QR кода в области поиска штампа без OpenCV
        
        Args:
            pdf_path: Путь к PDF файлу
            page_number: Номер страницы (начиная с 0)
            
        Returns:
            Словарь с координатами позиции QR кода или None
        """
        try:
            self.logger.debug("🔄 Using fallback QR positioning in stamp region")
            
            doc = fitz.open(pdf_path)
            if page_number >= len(doc):
                self.logger.error("❌ Page number out of range in fallback", 
                                page_number=page_number, total_pages=len(doc))
                return None
                
            page = doc[page_number]
            page_rect = page.rect
            page_width = page_rect.width
            page_height = page_rect.height
            
            # Размер QR кода
            qr_size_cm = 3.5
            qr_size_points = qr_size_cm * 28.35
            
            # Fallback: ставим QR на 1 см от правого края и 1 см от нижнего края
            x_position = page_width - qr_size_points - (1.0 * 28.35)  # 1 см от правого края
            y_position = page_height - qr_size_points - (1.0 * 28.35)  # 1 см от нижнего края
            
            result = {
                "x": x_position,
                "y": y_position,
                "width": qr_size_points,
                "height": qr_size_points
            }
            
            self.logger.info("✅ Fallback QR position calculated in stamp region", 
                           x=result["x"], y=result["y"],
                           x_cm=round(result["x"] / 28.35, 2),
                           y_cm=round(result["y"] / 28.35, 2))
            
            doc.close()
            return result
            
        except Exception as e:
            self.logger.error("Error in fallback QR positioning in stamp region", error=str(e))
            return None
