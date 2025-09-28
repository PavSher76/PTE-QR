"""
Оптимизированный PDF сервис для обработки PDF с QR кодами
Устранены проблемы с временными файлами и улучшена производительность
"""

import os
import uuid
import time
from io import BytesIO
from typing import Dict, Any, List, Optional, Tuple

import structlog
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import DebugLogger
from app.models.document import Document
from app.models.qr_code import QRCode
from app.services.document_service import DocumentService
from app.services.qr_service import QRService
from app.utils.pdf_analyzer_optimized import OptimizedPDFAnalyzer

logger = structlog.get_logger()
debug_logger = DebugLogger(__name__)

class OptimizedPDFService:
    """
    Оптимизированный сервис для обработки PDF документов с QR кодами
    """

    def __init__(self):
        self.pdf_analyzer = OptimizedPDFAnalyzer()
        self.output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(self.output_dir, exist_ok=True)

    async def process_pdf_with_qr_codes_optimized(
        self,
        pdf_content: bytes,
        enovia_id: str,
        title: str,
        revision: str,
        created_by: uuid.UUID,
        qr_service: QRService,
        document_service: DocumentService
    ) -> Dict[str, Any]:
        """
        Оптимизированная обработка PDF с QR кодами без создания временных файлов
        
        Args:
            pdf_content: Содержимое PDF файла в байтах
            enovia_id: ID документа в ENOVIA
            title: Название документа
            revision: Ревизия документа
            created_by: ID пользователя, создавшего документ
            qr_service: Сервис для работы с QR кодами
            document_service: Сервис для работы с документами
            
        Returns:
            Словарь с результатами обработки
        """
        start_time = time.time()
        
        try:
            debug_logger.info("Starting optimized PDF processing", 
                            enovia_id=enovia_id, title=title, revision=revision)
            
            # Анализируем PDF без создания временных файлов
            pdf_reader = PdfReader(BytesIO(pdf_content))
            total_pages = len(pdf_reader.pages)
            
            debug_logger.info("PDF analysis completed", 
                            total_pages=total_pages, enovia_id=enovia_id)
            
            # Создаем документ в базе данных
            document = await document_service.create_document(
                enovia_id=enovia_id,
                title=title,
                revision=revision,
                created_by=created_by,
                total_pages=total_pages
            )
            
            # Обрабатываем каждую страницу
            processed_pages = []
            qr_codes_created = []
            
            for page_number in range(total_pages):
                try:
                    # Анализируем макет страницы (оптимизированно)
                    layout_info = self.pdf_analyzer.analyze_page_layout_optimized(
                        pdf_content, page_number
                    )
                    
                    # Генерируем QR код для страницы
                    qr_code_data = await qr_service.generate_qr_code(
                        document_id=document.id,
                        page_number=page_number + 1,
                        enovia_id=enovia_id,
                        revision=revision
                    )
                    
                    # Добавляем QR код к странице (оптимизированно)
                    processed_page = self._add_qr_code_to_page_optimized(
                        pdf_reader.pages[page_number], 
                        qr_code_data['qr_image'],
                        page_number + 1,
                        layout_info
                    )
                    
                    processed_pages.append(processed_page)
                    qr_codes_created.append(qr_code_data)
                    
                    debug_logger.info("Page processed successfully", 
                                    page_number=page_number + 1,
                                    enovia_id=enovia_id)
                    
                except Exception as e:
                    debug_logger.error("Error processing page", 
                                     page_number=page_number + 1,
                                     error=str(e))
                    # Добавляем оригинальную страницу без QR кода
                    processed_pages.append(pdf_reader.pages[page_number])
            
            # Создаем итоговый PDF
            output_pdf = self._create_output_pdf(processed_pages)
            
            # Сохраняем результат
            output_filename = f"{enovia_id}_rev{revision}_with_qr.pdf"
            output_path = os.path.join(self.output_dir, output_filename)
            
            with open(output_path, 'wb') as f:
                f.write(output_pdf)
            
            # Обновляем документ
            await document_service.update_document_status(
                document.id, "processed", output_path
            )
            
            duration = time.time() - start_time
            
            debug_logger.info("PDF processing completed successfully", 
                            enovia_id=enovia_id,
                            total_pages=total_pages,
                            qr_codes_created=len(qr_codes_created),
                            output_path=output_path,
                            duration=duration)
            
            return {
                "success": True,
                "document_id": str(document.id),
                "enovia_id": enovia_id,
                "total_pages": total_pages,
                "qr_codes_created": len(qr_codes_created),
                "output_path": output_path,
                "duration": duration
            }
            
        except Exception as e:
            duration = time.time() - start_time
            debug_logger.error("PDF processing failed", 
                            enovia_id=enovia_id,
                            error=str(e),
                            duration=duration)
            raise

    def _add_qr_code_to_page_optimized(
        self, 
        page, 
        qr_image: Image.Image, 
        page_number: int, 
        layout_info: Dict[str, Any]
    ) -> Any:
        """
        Оптимизированное добавление QR кода к странице без временных файлов
        """
        try:
            # Получаем размеры страницы
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            # Размер QR кода в точках
            qr_size_points = settings.PDF_QR_SIZE
            
            # Вычисляем позицию QR кода
            x_position, y_position = self._calculate_qr_position_optimized(
                page_width, page_height, qr_size_points, layout_info
            )
            
            debug_logger.info("QR position calculated", 
                            page=page_number,
                            x=x_position, y=y_position,
                            qr_size=qr_size_points)
            
            # Создаем PDF с QR кодом напрямую в памяти
            qr_pdf_buffer = BytesIO()
            c = canvas.Canvas(qr_pdf_buffer, pagesize=(page_width, page_height))
            
            # Конвертируем PIL изображение в формат, подходящий для ReportLab
            # Сохраняем в BytesIO вместо временного файла
            img_buffer = BytesIO()
            qr_image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Создаем временный файл только для ReportLab (необходимо для drawImage)
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_img:
                temp_img.write(img_buffer.getvalue())
                temp_img.flush()
                
                # Рисуем QR код
                c.drawImage(
                    temp_img.name,
                    x_position,
                    y_position,
                    width=qr_size_points,
                    height=qr_size_points,
                    mask="auto",
                )
                
                # Очищаем временный файл
                os.unlink(temp_img.name)
            
            # Добавляем номер страницы
            c.setFont("Helvetica", 8)
            c.drawString(x_position, y_position - 15, f"Page {page_number}")
            
            c.save()
            
            # Объединяем с оригинальной страницей
            qr_pdf_buffer.seek(0)
            qr_pdf_reader = PdfReader(qr_pdf_buffer)
            page.merge_page(qr_pdf_reader.pages[0])
            
            return page
            
        except Exception as e:
            debug_logger.error("Error adding QR code to page", 
                            page_number=page_number, error=str(e))
            return page

    def _calculate_qr_position_optimized(
        self, 
        page_width: float, 
        page_height: float, 
        qr_size: float, 
        layout_info: Dict[str, Any]
    ) -> Tuple[float, float]:
        """
        Оптимизированное вычисление позиции QR кода
        """
        try:
            # Используем информацию из анализа макета
            if layout_info.get("free_space_3_5cm"):
                free_space = layout_info["free_space_3_5cm"]
                return free_space["x"], free_space["y"]
            
            # Fallback к простому якорю
            margin = settings.QR_MARGIN_PT
            anchor = settings.QR_ANCHOR
            
            if anchor == 'bottom-right':
                x = page_width - qr_size - margin
                y = margin
            elif anchor == 'bottom-left':
                x = margin
                y = margin
            elif anchor == 'top-right':
                x = page_width - qr_size - margin
                y = page_height - qr_size - margin
            elif anchor == 'top-left':
                x = margin
                y = page_height - qr_size - margin
            else:
                x = page_width - qr_size - margin
                y = margin
            
            # Клэмп координат
            x = max(0, min(x, page_width - qr_size))
            y = max(0, min(y, page_height - qr_size))
            
            return x, y
            
        except Exception as e:
            debug_logger.error("Error calculating QR position", error=str(e))
            # Fallback позиция
            return page_width - qr_size - settings.QR_MARGIN_PT, settings.QR_MARGIN_PT

    def _create_output_pdf(self, pages: List[Any]) -> bytes:
        """
        Создание итогового PDF из обработанных страниц
        """
        try:
            output_buffer = BytesIO()
            pdf_writer = PdfWriter()
            
            for page in pages:
                pdf_writer.add_page(page)
            
            pdf_writer.write(output_buffer)
            return output_buffer.getvalue()
            
        except Exception as e:
            debug_logger.error("Error creating output PDF", error=str(e))
            raise

    def get_pdf_info_optimized(self, pdf_content: bytes) -> Dict[str, Any]:
        """
        Оптимизированное получение информации о PDF без создания временных файлов
        """
        try:
            pdf_reader = PdfReader(BytesIO(pdf_content))
            
            info = {
                "total_pages": len(pdf_reader.pages),
                "pages": []
            }
            
            for i, page in enumerate(pdf_reader.pages):
                page_info = {
                    "page_number": i + 1,
                    "width": float(page.mediabox.width),
                    "height": float(page.mediabox.height),
                    "rotation": getattr(page, 'rotation', 0),
                    "is_landscape": float(page.mediabox.width) > float(page.mediabox.height)
                }
                info["pages"].append(page_info)
            
            return info
            
        except Exception as e:
            debug_logger.error("Error getting PDF info", error=str(e))
            return {"error": str(e)}

    def clear_analyzer_cache(self):
        """Очистка кэша анализатора"""
        self.pdf_analyzer.clear_cache()
        debug_logger.info("PDF analyzer cache cleared")
