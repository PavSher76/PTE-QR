"""
Полностью переработанный PDF сервис для максимальной эффективности
Работает только с pdf_content в памяти, без временных файлов
"""

import structlog
import time
from typing import Dict, Any, List, Optional, Tuple
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import cm
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.lib.colors import black, white

from app.core.config import settings
from app.utils.pdf_analyzer_v2 import PDFAnalyzerV2
from app.utils.pdf_exceptions import PDFAnalysisError, PDFFileError
from app.services.qr_service import QRService

logger = structlog.get_logger()


class PDFServiceV2:
    """
    Полностью переработанный PDF сервис
    - Работает только с pdf_content в памяти
    - Максимальная производительность
    - Улучшенная отладка
    - Без временных файлов
    """
    
    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        self.pdf_analyzer = PDFAnalyzerV2()
        self.qr_service = QRService()
        
        # Статистика сервиса
        self.service_stats = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "average_operation_time": 0.0,
            "qr_codes_generated": 0,
            "pages_processed": 0
        }
    
    def _validate_pdf_content(self, pdf_content: bytes) -> None:
        """Валидация PDF содержимого"""
        if not pdf_content:
            raise PDFFileError("PDF content is empty", file_size=0)
        
        if len(pdf_content) < 100:
            raise PDFFileError(
                f"PDF file is too small: {len(pdf_content)} bytes",
                file_size=len(pdf_content)
            )
        
        if not pdf_content.startswith(b'%PDF'):
            raise PDFFileError("Invalid PDF file format")
    
    def _get_page_info(self, pdf_content: bytes) -> Dict[str, Any]:
        """Получение информации о страницах PDF"""
        try:
            doc = PdfReader(BytesIO(pdf_content))
            pages_info = []
            
            for i, page in enumerate(doc.pages):
                page_info = {
                    "page_number": i,
                    "width": float(page.mediabox.width),
                    "height": float(page.mediabox.height),
                    "rotation": getattr(page, 'rotation', 0) % 360,
                    "is_landscape": float(page.mediabox.width) > float(page.mediabox.height)
                }
                pages_info.append(page_info)
            
            return {
                "total_pages": len(pages_info),
                "pages": pages_info
            }
            
        except Exception as e:
            raise PDFAnalysisError(f"Failed to get page info: {str(e)}")
    
    def _generate_qr_image_data(self, qr_data: str, size_cm: float = 3.5) -> bytes:
        """Генерация QR кода в виде PNG данных"""
        try:
            qr_image = self.qr_service.generate_qr_code(qr_data, size_cm=size_cm)
            
            # Конвертируем PIL Image в PNG bytes
            img_buffer = BytesIO()
            qr_image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            return img_buffer.getvalue()
            
        except Exception as e:
            self.logger.error("Failed to generate QR code", error=str(e), qr_data=qr_data)
            raise PDFAnalysisError(f"Failed to generate QR code: {str(e)}")
    
    def _add_qr_to_page_memory(self, pdf_content: bytes, page_number: int, 
                              qr_data: str, position: Dict[str, float]) -> bytes:
        """
        Добавление QR кода к странице PDF в памяти
        """
        try:
            # Генерируем QR код
            qr_image_data = self._generate_qr_image_data(qr_data, size_cm=3.5)
            
            # Открываем PDF
            doc = PdfReader(BytesIO(pdf_content))
            if page_number >= len(doc.pages):
                raise PDFAnalysisError(f"Page {page_number} out of range")
            
            page = doc.pages[page_number]
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            # Создаем новый PDF с QR кодом
            output_buffer = BytesIO()
            writer = PdfWriter()
            
            # Копируем все страницы
            for i, src_page in enumerate(doc.pages):
                if i == page_number:
                    # Добавляем QR код к целевой странице
                    new_page = self._add_qr_to_single_page(src_page, qr_image_data, position)
                    writer.add_page(new_page)
                else:
                    writer.add_page(src_page)
            
            # Записываем результат
            writer.write(output_buffer)
            output_buffer.seek(0)
            
            return output_buffer.getvalue()
            
        except Exception as e:
            self.logger.error("Failed to add QR to page", 
                            error=str(e), page_number=page_number)
            raise PDFAnalysisError(f"Failed to add QR to page: {str(e)}")
    
    def _add_qr_to_single_page(self, page, qr_image_data: bytes, 
                              position: Dict[str, float]) -> Any:
        """
        Добавление QR кода к одной странице
        """
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.units import cm
            from reportlab.graphics import renderPDF
            from reportlab.graphics.shapes import Drawing, Rect
            from reportlab.lib.colors import black, white
            from PIL import Image
            import io
            
            # Создаем временный PDF с QR кодом
            qr_buffer = BytesIO()
            c = canvas.Canvas(qr_buffer, pagesize=letter)
            
            # Получаем размеры страницы
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            # Создаем изображение QR кода
            qr_image = Image.open(io.BytesIO(qr_image_data))
            
            # Сохраняем QR код как временный файл для ReportLab
            temp_qr_buffer = BytesIO()
            qr_image.save(temp_qr_buffer, format='PNG')
            temp_qr_buffer.seek(0)
            
            # Добавляем QR код на страницу
            c.drawImage(temp_qr_buffer, 
                       position["x"], position["y"],
                       width=position["width"], height=position["height"])
            
            c.save()
            qr_buffer.seek(0)
            
            # Создаем PDF с QR кодом
            qr_pdf = PdfReader(qr_buffer)
            qr_page = qr_pdf.pages[0]
            
            # Объединяем страницы
            page.merge_page(qr_page)
            
            return page
            
        except Exception as e:
            self.logger.error("Failed to add QR to single page", error=str(e))
            raise PDFAnalysisError(f"Failed to add QR to single page: {str(e)}")
    
    def _calculate_qr_positions(self, pdf_content: bytes, qr_data_list: List[str]) -> List[Dict[str, Any]]:
        """
        Расчет позиций QR кодов для всех страниц
        """
        try:
            page_info = self._get_page_info(pdf_content)
            qr_positions = []
            
            for i, qr_data in enumerate(qr_data_list):
                if i >= page_info["total_pages"]:
                    self.logger.warning("More QR codes than pages", 
                                      qr_count=len(qr_data_list), 
                                      page_count=page_info["total_pages"])
                    break
                
                # Анализируем макет страницы
                layout_info = self.pdf_analyzer.analyze_page_layout(pdf_content, i)
                
                # Получаем позицию QR кода
                qr_position = layout_info.get("detected_elements", {}).get("qr_position")
                
                if not qr_position:
                    # Fallback позиция
                    page = page_info["pages"][i]
                    qr_position = {
                        "x": page["width"] - 100,
                        "y": 50,
                        "width": 100,
                        "height": 100
                    }
                
                qr_positions.append({
                    "page_number": i,
                    "qr_data": qr_data,
                    "position": qr_position,
                    "layout_info": layout_info
                })
            
            return qr_positions
            
        except Exception as e:
            self.logger.error("Failed to calculate QR positions", error=str(e))
            raise PDFAnalysisError(f"Failed to calculate QR positions: {str(e)}")
    
    def add_qr_codes_to_pdf(self, pdf_content: bytes, qr_data_list: List[str]) -> bytes:
        """
        Добавление QR кодов к PDF документу
        """
        start_time = time.time()
        operation_success = False
        
        try:
            self.logger.info("Starting QR code addition to PDF", 
                           qr_count=len(qr_data_list),
                           content_size=len(pdf_content))
            
            # Валидация входных данных
            self._validate_pdf_content(pdf_content)
            
            if not qr_data_list:
                raise PDFAnalysisError("QR data list is empty")
            
            # Получаем информацию о страницах
            page_info = self._get_page_info(pdf_content)
            
            if len(qr_data_list) > page_info["total_pages"]:
                self.logger.warning("More QR codes than pages, truncating", 
                                  qr_count=len(qr_data_list), 
                                  page_count=page_info["total_pages"])
                qr_data_list = qr_data_list[:page_info["total_pages"]]
            
            # Рассчитываем позиции QR кодов
            qr_positions = self._calculate_qr_positions(pdf_content, qr_data_list)
            
            # Добавляем QR коды к страницам
            result_pdf_content = pdf_content
            
            for qr_info in qr_positions:
                result_pdf_content = self._add_qr_to_page_memory(
                    result_pdf_content,
                    qr_info["page_number"],
                    qr_info["qr_data"],
                    qr_info["position"]
                )
                
                self.service_stats["qr_codes_generated"] += 1
                self.service_stats["pages_processed"] += 1
            
            operation_success = True
            operation_time = time.time() - start_time
            
            self.logger.info("QR codes added to PDF successfully", 
                           qr_count=len(qr_positions),
                           operation_time=operation_time,
                           result_size=len(result_pdf_content))
            
            return result_pdf_content
            
        except Exception as e:
            operation_time = time.time() - start_time
            self.logger.error("Failed to add QR codes to PDF", 
                            error=str(e),
                            operation_time=operation_time)
            raise
            
        finally:
            # Обновляем статистику
            self.service_stats["total_operations"] += 1
            if operation_success:
                self.service_stats["successful_operations"] += 1
            else:
                self.service_stats["failed_operations"] += 1
            
            # Обновляем среднее время операции
            total_successful = self.service_stats["successful_operations"]
            if total_successful > 0:
                current_avg = self.service_stats["average_operation_time"]
                self.service_stats["average_operation_time"] = (
                    (current_avg * (total_successful - 1) + operation_time) / total_successful
                )
    
    def analyze_pdf_layout(self, pdf_content: bytes, page_number: int = 0) -> Dict[str, Any]:
        """
        Анализ макета PDF страницы
        """
        try:
            self.logger.debug("Analyzing PDF layout", 
                            page_number=page_number,
                            content_size=len(pdf_content))
            
            # Валидация входных данных
            self._validate_pdf_content(pdf_content)
            
            # Анализируем макет страницы
            layout_info = self.pdf_analyzer.analyze_page_layout(pdf_content, page_number)
            
            self.logger.info("PDF layout analysis completed", 
                           page_number=page_number,
                           layout_info=layout_info)
            
            return layout_info
            
        except Exception as e:
            self.logger.error("Failed to analyze PDF layout", 
                            error=str(e), page_number=page_number)
            raise
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Получение статистики сервиса"""
        return {
            **self.service_stats,
            "analyzer_stats": self.pdf_analyzer.get_analysis_stats(),
            "qr_service_stats": getattr(self.qr_service, 'get_stats', lambda: {})()
        }
    
    def clear_cache(self):
        """Очистка кэша"""
        self.pdf_analyzer.clear_cache()
        self.logger.debug("Service cache cleared")
    
    def update_analyzer_config(self, config_updates: Dict[str, Any]) -> None:
        """Обновление конфигурации анализатора"""
        self.pdf_analyzer.update_config(config_updates)
        self.logger.info("Analyzer configuration updated", config_updates=config_updates)
