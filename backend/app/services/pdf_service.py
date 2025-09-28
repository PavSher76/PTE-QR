"""
Service for PDF processing and QR code integration
"""

import os
import tempfile
import uuid
from copy import deepcopy
from typing import Dict, Any, List
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from io import BytesIO
import structlog
from PIL import Image

from app.services.qr_service import QRService
from app.services.document_service import DocumentService
from app.core.config import settings
from app.core.logging import DebugLogger, log_function_call, log_function_result, log_file_operation
from app.utils.pdf_analyzer import PDFAnalyzer

logger = structlog.get_logger()
debug_logger = DebugLogger(__name__)

class PDFService:
    """Service for PDF processing and QR code integration"""

    def __init__(self):
        log_function_call("PDFService.__init__")
        # Use temp directory for local development
        self.output_dir = os.path.join(tempfile.gettempdir(), "pte_qr_pdf_output")
        os.makedirs(self.output_dir, exist_ok=True)
        self.pdf_analyzer = PDFAnalyzer()
        debug_logger.info("PDFService initialized", output_dir=self.output_dir)
        log_function_result("PDFService.__init__", output_dir=self.output_dir)

    async def process_pdf_with_qr_codes(
        self,
        pdf_path: str,
        enovia_id: str,
        title: str,
        revision: str,
        created_by: uuid.UUID,
        qr_service: QRService,
        document_service: DocumentService
    ) -> Dict[str, Any]:
        """
        Process PDF file and add QR codes to each page
        """
        log_function_call(
            "PDFService.process_pdf_with_qr_codes",
            pdf_path=pdf_path,
            enovia_id=enovia_id,
            title=title,
            revision=revision,
            created_by=str(created_by)
        )
        
        try:
            debug_logger.info(
                "Starting PDF processing with QR codes",
                pdf_path=pdf_path,
                enovia_id=enovia_id,
                title=title,
                revision=revision,
                created_by=str(created_by)
            )
            
            # Check if PDF file exists
            if not os.path.exists(pdf_path):
                debug_logger.error("PDF file not found", pdf_path=pdf_path)
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            log_file_operation("read", pdf_path, file_size=os.path.getsize(pdf_path))
            
            # Read the PDF
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)
            
            debug_logger.info(
                "PDF loaded successfully",
                total_pages=total_pages,
                enovia_id=enovia_id,
                title=title,
                revision=revision
            )

            # Create or update document in database
            debug_logger.debug("Creating/updating document in database", enovia_id=enovia_id)
            document = await document_service.create_or_update_document(
                enovia_id=enovia_id,
                title=title,
                revision=revision,
                total_pages=total_pages,
                created_by=created_by
            )
            debug_logger.info("Document created/updated", document_id=str(document.id))

            # Create output PDF writer
            writer = PdfWriter()
            qr_codes_created = 0

            debug_logger.info("Starting page processing", total_pages=total_pages)

            # Process each page
            for page_num in range(total_pages):
                debug_logger.debug("Processing page", page_number=page_num + 1, total_pages=total_pages)
                page = reader.pages[page_num]
                
                # Check page orientation first
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)
                is_landscape = page_width > page_height
                
                if not is_landscape:
                    # For Portrait pages: Skip QR code placement
                    debug_logger.info(f"Portrait page detected - skipping QR code placement (portrait pages not supported)", page_number=page_num + 1)
                    writer.add_page(page)  # Add original page without QR code
                    continue
                
                # Generate QR code for this page (only for landscape pages)
                debug_logger.debug("Generating QR code data", page_number=page_num + 1)
                qr_data = qr_service.generate_qr_data(
                    enovia_id=enovia_id,
                    revision=revision,
                    page_number=page_num + 1
                )
                
                # Create QR code image
                debug_logger.debug("Creating QR code image", page_number=page_num + 1)
                qr_image = qr_service.generate_qr_code_image(qr_data)
                
                # Add QR code to page
                debug_logger.debug("Adding QR code to page", page_number=page_num + 1)
                page_with_qr = self._add_qr_code_to_page(page, qr_image, page_num + 1, pdf_path)
                writer.add_page(page_with_qr)
                
                # Save QR code to database
                debug_logger.debug("Saving QR code to database", page_number=page_num + 1)
                await document_service.create_qr_code(
                    document_id=document.id,
                    enovia_id=enovia_id,
                    revision=revision,
                    page_number=page_num + 1,
                    qr_data=qr_data,
                    created_by=created_by
                )
                
                qr_codes_created += 1
                debug_logger.debug("Page processed successfully", page_number=page_num + 1, qr_codes_created=qr_codes_created)

            # Save the output PDF
            output_filename = f"{enovia_id}_{revision}_{uuid.uuid4().hex[:8]}.pdf"
            output_path = os.path.join(self.output_dir, output_filename)
            
            debug_logger.info("Saving output PDF", output_path=output_path, output_filename=output_filename)
            log_file_operation("write", output_path)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            # Get file size for logging
            output_file_size = os.path.getsize(output_path)
            
            debug_logger.info(
                "PDF processing completed successfully",
                enovia_id=enovia_id,
                pages_processed=total_pages,
                qr_codes_created=qr_codes_created,
                output_file=output_filename,
                output_file_size=output_file_size
            )

            result = {
                "document_id": document.id,
                "qr_codes_count": qr_codes_created,
                "pages_processed": total_pages,
                "output_file": output_filename
            }
            
            log_function_result(
                "PDFService.process_pdf_with_qr_codes",
                result=result,
                enovia_id=enovia_id,
                pages_processed=total_pages,
                qr_codes_created=qr_codes_created
            )
            
            return result

        except Exception as e:
            debug_logger.exception(
                "Error processing PDF",
                error=str(e),
                enovia_id=enovia_id,
                pdf_path=pdf_path
            )
            raise

    def _add_qr_code_to_page(self, page, qr_image, page_number: int, pdf_path: str = None):
        """
        Add QR code to a PDF page with intelligent positioning
        """
        log_function_call("PDFService._add_qr_code_to_page", page_number=page_number)
        
        try:
            debug_logger.debug("Adding QR code to page", page_number=page_number)
            # Create a new page with QR code overlay
            packet = BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            
            # QR code size: 3.5 cm x 3.5 cm as per requirements
            # Convert cm to points: 1 cm = 28.35 points
            qr_size_cm = 3.5
            qr_size = qr_size_cm * 28.35  # 99.225 points
            
            # Use new unified positioning system
            x_position, y_position = self._calculate_unified_qr_position(
                page, qr_size, pdf_path, page_number - 1
            )
            
            # Get page dimensions for audit (используем MediaBox для консистентности)
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            active_box_type = "media"
            
            # COORDINATE PIPELINE AUDIT - Log all parameters before insertion
            debug_logger.info("🔍 COORDINATE PIPELINE AUDIT - Before QR insertion", 
                            page=page_number,
                            box=active_box_type,
                            W=page_width,
                            H=page_height,
                            rotation="TBD",  # Will be filled by _calculate_unified_qr_position
                            qr=(qr_size, qr_size),
                            margin="TBD",  # Will be filled by _calculate_unified_qr_position
                            x_position=x_position,
                            y_position=y_position,
                            x_cm=round(x_position / 28.35, 2),
                            y_cm=round(y_position / 28.35, 2))
            
            # Draw QR code
            can.drawImage(qr_image, x_position, y_position, 
                         width=qr_size, height=qr_size)
            
            # Add page number text
            can.setFont("Helvetica", 8)
            can.drawString(x_position, y_position - 15, f"Page {page_number}")
            
            can.save()
            
            # Move to beginning of StringIO buffer
            packet.seek(0)
            new_pdf = PdfReader(packet)
            
            # Merge the QR code page with the original page
            page.merge_page(new_pdf.pages[0])
            
            return page
            
        except Exception as e:
            logger.error(f"Error adding QR code to page {page_number}", error=str(e))
            # Return original page if QR code addition fails
            return page

    def _calculate_unified_qr_position(self, page, qr_size: float, pdf_path: str, page_number: int) -> tuple[float, float]:
        """
        Унифицированный расчет позиции QR кода без двойной инверсии
        
        Args:
            page: Страница PDF (PyPDF2)
            qr_size: Размер QR кода в точках
            pdf_path: Путь к PDF файлу для анализа
            page_number: Номер страницы (0-indexed)
            
        Returns:
            Tuple of (x_position, y_position) in PDF points (origin bottom-left)
        """
        try:
            debug_logger.debug("Calculating unified QR position", 
                             qr_size=qr_size, pdf_path=pdf_path, page_number=page_number)
            
            # Анализируем макет страницы для получения координатной информации
            layout_info = self.pdf_analyzer.analyze_page_layout(pdf_path, page_number)
            
            if not layout_info:
                debug_logger.warning("Could not analyze page layout, using fallback position")
                # Fallback: используем базовый якорь без эвристик
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)
                rotation = 0  # Предполагаем поворот 0° для fallback
                
                base_x, base_y = self.compute_anchor_xy(
                    W=page_width,
                    H=page_height,
                    qr_w=qr_size,
                    qr_h=qr_size,
                    margin=settings.QR_MARGIN_PT,
                    rotation=rotation,
                    anchor=settings.QR_ANCHOR
                )
                
                debug_logger.info("🔍 FALLBACK - Base anchor only", 
                                page=page_number,
                                box="media",
                                W=page_width,
                                H=page_height,
                                rot=rotation,
                                anchor=settings.QR_ANCHOR,
                                qr=(qr_size, qr_size),
                                margin=settings.QR_MARGIN_PT,
                                base=(base_x, base_y),
                                delta=(0.0, 0.0),
                                final=(base_x, base_y))
                
                return base_x, base_y
            
            # Получаем информацию о координатах
            coordinate_info = layout_info.get("coordinate_info", {})
            active_box = coordinate_info.get("active_box", {})
            rotation = coordinate_info.get("rotation", 0)
            
            # 1. СНАЧАЛА вычисляем базовый якорь bottom-right с учетом rotation
            page_width = active_box.get("width", float(page.mediabox.width))
            page_height = active_box.get("height", float(page.mediabox.height))
            
            base_x, base_y = self.compute_anchor_xy(
                W=page_width,
                H=page_height, 
                qr_w=qr_size,
                qr_h=qr_size,
                margin=settings.QR_MARGIN_PT,
                rotation=rotation,
                anchor=settings.QR_ANCHOR
            )
            
            # 2. ПОТОМ получаем дельту от эвристик (если нужно)
            dx, dy = self.pdf_analyzer.compute_heuristics_delta(pdf_path, page_number)
            
            # 3. Применяем дельту к базовому якорю
            x_position = base_x + dx
            y_position = base_y + dy
            
            # 4. Клэмпим координаты в пределах страницы
            x_position = max(0, min(x_position, page_width - qr_size))
            y_position = max(0, min(y_position, page_height - qr_size))
            
            # COORDINATE PIPELINE AUDIT - Detailed calculation info
            debug_logger.info("🔍 COORDINATE PIPELINE AUDIT - Detailed calculation", 
                            page=page_number,
                            box=coordinate_info.get("active_box_type", "media"),
                            W=page_width,
                            H=page_height,
                            rot=rotation,
                            anchor=settings.QR_ANCHOR,
                            qr=(qr_size, qr_size),
                            margin=settings.QR_MARGIN_PT,
                            base=(base_x, base_y),
                            delta=(dx, dy),
                            final=(x_position, y_position),
                            respect_rotation=settings.QR_RESPECT_ROTATION)
            
            # Отрисовываем debug рамку если включено
            if hasattr(self.pdf_analyzer, '_draw_debug_frame'):
                debug_file = self.pdf_analyzer._draw_debug_frame(
                    pdf_path, page_number, x_position, y_position, qr_size, qr_size
                )
                if debug_file:
                    debug_logger.debug("Debug frame saved", debug_file=debug_file)
            
            return x_position, y_position
            
        except Exception as e:
            debug_logger.error("Error calculating unified QR position", 
                             error=str(e), pdf_path=pdf_path, page_number=page_number)
            # Fallback: используем базовый якорь без эвристик
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            rotation = 0  # Предполагаем поворот 0° для fallback
            
            base_x, base_y = self.compute_anchor_xy(
                W=page_width,
                H=page_height,
                qr_w=qr_size,
                qr_h=qr_size,
                margin=settings.QR_MARGIN_PT,
                rotation=rotation,
                anchor=settings.QR_ANCHOR
            )
            
            debug_logger.info("🔍 EXCEPTION FALLBACK - Base anchor only", 
                            page=page_number,
                            box="media",
                            W=page_width,
                            H=page_height,
                            rot=rotation,
                            anchor=settings.QR_ANCHOR,
                            qr=(qr_size, qr_size),
                            margin=settings.QR_MARGIN_PT,
                            base=(base_x, base_y),
                            delta=(0.0, 0.0),
                            final=(base_x, base_y))
            
            return base_x, base_y

    def _calculate_landscape_qr_position(self, page_width: float, page_height: float, 
                                       qr_size: float, pdf_path: str, page_number: int) -> tuple[float, float]:
        """
        Calculate intelligent QR code position for landscape pages using new algorithm
        
        New positioning logic:
        1. Search for free space 3.5x3.5 cm in bottom-left corner
        2. Along horizontal line of at least 18 cm length
        3. Along right vertical frame of the drawing
        
        Args:
            page_width: Width of the page in points
            page_height: Height of the page in points
            qr_size: Size of QR code in points
            pdf_path: Path to PDF file for analysis
            page_number: Page number (0-indexed)
            
        Returns:
            Tuple of (x_position, y_position) in points
        """
        try:
            debug_logger.debug("Calculating landscape QR position with new algorithm", 
                             page_width=page_width, page_height=page_height, 
                             qr_size=qr_size, pdf_path=pdf_path, page_number=page_number)
            
            # Default fallback position (bottom-left corner)
            default_x = 0.5 * 28.35  # 0.5 cm from left edge
            default_y = 0.5 * 28.35  # 0.5 cm up from bottom
            
            if not pdf_path or not os.path.exists(pdf_path):
                debug_logger.warning("PDF path not available for analysis, using default position")
                return default_x, default_y
            
            # Analyze page layout to detect elements and free space
            layout_info = self.pdf_analyzer.analyze_page_layout(pdf_path, page_number)
            
            if not layout_info:
                debug_logger.warning("Could not analyze page layout, using default position")
                return default_x, default_y
            
            # 1. СНАЧАЛА вычисляем базовый якорь bottom-right
            base_x, base_y = self.compute_anchor_xy(
                W=page_width,
                H=page_height,
                qr_w=qr_size,
                qr_h=qr_size,
                margin=settings.QR_MARGIN_PT,
                rotation=0,  # Предполагаем поворот 0° для landscape
                anchor=settings.QR_ANCHOR
            )
            
            # 2. ПОТОМ получаем дельту от эвристик
            dx, dy = self.pdf_analyzer.compute_heuristics_delta(pdf_path, page_number)
            
            # 3. Применяем дельту к базовому якорю
            x_position = base_x + dx
            y_position = base_y + dy
            
            # 4. Клэмпим координаты в пределах страницы
            x_position = max(0, min(x_position, page_width - qr_size))
            y_position = max(0, min(y_position, page_height - qr_size))
            
            debug_logger.info("🔍 LANDSCAPE - Base anchor + heuristics delta", 
                            page=page_number,
                            box="media",
                            W=page_width,
                            H=page_height,
                            rot=0,
                            anchor=settings.QR_ANCHOR,
                            qr=(qr_size, qr_size),
                            margin=settings.QR_MARGIN_PT,
                            base=(base_x, base_y),
                            delta=(dx, dy),
                            final=(x_position, y_position))
            
            return x_position, y_position
            
        except Exception as e:
            debug_logger.error("Error calculating landscape QR position", 
                             error=str(e), pdf_path=pdf_path, page_number=page_number)
            # Fallback: используем базовый якорь без эвристик
            base_x, base_y = self.compute_anchor_xy(
                W=page_width,
                H=page_height,
                qr_w=qr_size,
                qr_h=qr_size,
                margin=settings.QR_MARGIN_PT,
                rotation=0,
                anchor=settings.QR_ANCHOR
            )
            
            debug_logger.info("🔍 LANDSCAPE EXCEPTION FALLBACK - Base anchor only", 
                            page=page_number,
                            box="media",
                            W=page_width,
                            H=page_height,
                            rot=0,
                            anchor=settings.QR_ANCHOR,
                            qr=(qr_size, qr_size),
                            margin=settings.QR_MARGIN_PT,
                            base=(base_x, base_y),
                            delta=(0.0, 0.0),
                            final=(base_x, base_y))
            
            return base_x, base_y

    def get_pdf_info(self, pdf_path: str) -> Dict[str, Any]:
        """
        Get information about a PDF file
        """
        try:
            logger.debug("Getting PDF info", pdf_path=pdf_path)
            reader = PdfReader(pdf_path)
            return {
                "pages": len(reader.pages),
                "title": reader.metadata.get("/Title", "") if reader.metadata else "",
                "author": reader.metadata.get("/Author", "") if reader.metadata else "",
                "creator": reader.metadata.get("/Creator", "") if reader.metadata else "",
            }
        except Exception as e:
            logger.error(f"Error getting PDF info", error=str(e))
            raise

    async def add_qr_codes_to_pdf(
        self, pdf_content: bytes, enovia_id: str, revision: str, base_url_prefix: str
    ) -> tuple[bytes, list[dict]]:
        """
        Adds QR codes to each page of a PDF document.

        Args:
            pdf_content: The content of the PDF file as bytes.
            enovia_id: The ENOVIA ID of the document.
            revision: The revision of the document.
            base_url_prefix: The base URL prefix for QR code data.

        Returns:
            A tuple containing:
            - The processed PDF content with QR codes as bytes.
            - A list of dictionaries, each containing QR code data (page_number, qr_data, hmac_signature).
        """ 
        try:
            logger.debug("Adding QR codes to PDF", enovia_id=enovia_id, revision=revision, base_url_prefix=base_url_prefix)
            reader = PdfReader(BytesIO(pdf_content))
            writer = PdfWriter()
            qr_codes_data_list = []

            for i, page in enumerate(reader.pages):
                page_number = i + 1
                
                # Calculate position based on page orientation
                # Get actual page dimensions from the PDF page (используем MediaBox для консистентности)
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)
                
                # Determine page orientation
                is_landscape = page_width > page_height
                
                if not is_landscape:
                    # For Portrait pages: Skip QR code placement
                    logger.info(f"Portrait page detected - skipping QR code placement (portrait pages not supported)")
                    writer.add_page(page)  # Add original page without QR code
                    continue
                
                # Generate QR code data with HMAC signature (only for landscape pages)
                qr_data_payload = {
                    "enovia_id": enovia_id,
                    "revision": revision,
                    "page": page_number,
                }
                
                # Generate QR code data with HMAC signature
                qr_service = QRService()
                qr_data, hmac_signature = qr_service.generate_qr_data_with_hmac(
                    qr_data_payload, base_url_prefix
                )
                qr_codes_data_list.append(
                    {
                        "page_number": page_number,
                        "qr_data": qr_data,
                        "hmac_signature": hmac_signature,
                    }
                )

                # Generate QR code image
                # QR code size: 3.5 cm x 3.5 cm as per requirements
                # Convert cm to points: 1 cm = 28.35 points
                qr_size_cm = 3.5
                qr_size_points = qr_size_cm * 28.35  # 99.225 points
                
                qr_image_bytes = qr_service.generate_qr_code_image(
                    qr_data,
                    size=int(qr_size_points),  # 3.5 cm in points
                    border=4,  # Default border
                    error_correction='M',  # Default error correction
                )

                # Create a copy of the original page for modification
                modified_page = deepcopy(page)
                
                # Convert PIL Image to ReportLab Image
                pil_image = Image.open(BytesIO(qr_image_bytes))
                
                if is_landscape:
                    # For Landscape pages: Use intelligent positioning with PDF analysis
                    logger.info(f"Landscape page detected - using intelligent positioning with PDF analysis")
                    
                    # Create temporary file with single page for analysis
                    temp_writer = PdfWriter()
                    temp_writer.add_page(page)
                    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                        temp_writer.write(temp_pdf)
                        temp_pdf_path = temp_pdf.name
                    
                    try:
                        # Use intelligent positioning with PDF analysis
                        x_position, y_position = self._calculate_landscape_qr_position(
                            page_width, page_height, qr_size_points, temp_pdf_path, page_number - 1
                        )
                        logger.info(f"Landscape page detected - QR positioned intelligently at ({x_position:.1f}, {y_position:.1f})")
                    except Exception as e:
                        logger.warning(f"Intelligent positioning failed, using default: {e}")
                        # Fallback to default positioning
                        bottom_margin_cm = 5.5 + 0.5 + 3.5  # 5.5 hight of giggest main note, 0.5 bottom margin, 3.5 hight of QR code
                        right_margin_cm = 3.5 + 0.5    # 4 cm from left edge
                        
                        bottom_margin_points = bottom_margin_cm * 28.35
                        right_margin_points = right_margin_cm * 28.35
                        
                        x_position = page_width - right_margin_points - qr_size_points
                        y_position = page_height - bottom_margin_points - qr_size_points
                        
                        logger.info(f"Landscape page detected - QR positioned at bottom-right corner (fallback): {bottom_margin_cm}cm up from bottom, {right_margin_cm}cm from right edge")
                    finally:
                        # Clean up temporary file
                        if os.path.exists(temp_pdf_path):
                            os.unlink(temp_pdf_path)
                    
                    logger.info(f"QR positioning details: page_size=({page_width:.1f}x{page_height:.1f}), qr_size={qr_size_points:.1f}, position=({x_position:.1f}, {y_position:.1f})")

                # Save PIL image to temporary file for ReportLab
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_img:
                    pil_image.save(temp_img.name, format='PNG')
                    
                    # Create a new PDF with the QR code using the same page size as original
                    qr_pdf_buffer = BytesIO()
                    c = canvas.Canvas(qr_pdf_buffer, pagesize=(page_width, page_height))
                    
                    c.drawImage(
                        temp_img.name,
                        x_position,  # Draw at calculated position
                        y_position,  # Draw at calculated position
                        width=qr_size_points,
                        height=qr_size_points,
                        mask="auto",
                    )
                    
                    # Clean up temp file
                    os.unlink(temp_img.name)
                c.save()

                qr_pdf_buffer.seek(0)
                qr_pdf_reader = PdfReader(qr_pdf_buffer)
                qr_page = qr_pdf_reader.pages[0]

                # Merge the QR code page onto the modified page
                modified_page.merge_page(qr_page)
                writer.add_page(modified_page)

            output_pdf_buffer = BytesIO()
            writer.write(output_pdf_buffer)
            output_pdf_buffer.seek(0)

            return output_pdf_buffer.getvalue(), qr_codes_data_list
        except Exception as e:
            logger.error(f"Error adding QR codes to PDF", error=str(e))
            raise

    def compute_anchor_xy(self, W: float, H: float, qr_w: float, qr_h: float, 
                         margin: float, rotation: int, anchor: str = "bottom-right") -> tuple[float, float]:
        """
        Вычисляет координаты якоря с учетом поворота страницы
        
        Args:
            W: Ширина страницы в точках
            H: Высота страницы в точках
            qr_w: Ширина QR кода в точках
            qr_h: Высота QR кода в точках
            margin: Отступ в точках
            rotation: Поворот страницы в градусах (0, 90, 180, 270)
            anchor: Якорь позиционирования
            
        Returns:
            Tuple (x, y) координаты в PDF-СК (origin снизу-слева)
        """
        try:
            # Нормализуем поворот
            rotation = rotation % 360
            
            # Проверяем, нужно ли учитывать поворот
            if not settings.QR_RESPECT_ROTATION:
                rotation = 0
            
            # Вычисляем координаты по таблице поворотов
            if rotation == 0:
                if anchor == "bottom-right":
                    x = W - margin - qr_w
                    y = margin
                elif anchor == "bottom-left":
                    x = margin
                    y = margin
                elif anchor == "top-right":
                    x = W - margin - qr_w
                    y = H - margin - qr_h
                elif anchor == "top-left":
                    x = margin
                    y = H - margin - qr_h
                else:
                    debug_logger.warning(f"Unknown anchor '{anchor}', using 'bottom-right'")
                    x = W - margin - qr_w
                    y = margin
                    
            elif rotation == 180:
                # Поворот на 180°: визуальный нижний-правый
                x = margin
                y = H - margin - qr_h
                
            elif rotation == 90:
                # Поворот на 90°: визуальный нижний-правый
                x = margin
                y = margin
                
            elif rotation == 270:
                # Поворот на 270°: визуальный нижний-правый
                x = W - margin - qr_w
                y = H - margin - qr_h
                
            else:
                debug_logger.warning(f"Unsupported rotation {rotation}, using 0°")
                x = W - margin - qr_w
                y = margin
            
            # Клэмп координат
            x = max(0, min(x, W - qr_w))
            y = max(0, min(y, H - qr_h))
            
            debug_logger.debug("🎯 Anchor calculation", 
                            page="TBD",  # Будет заполнено вызывающим кодом
                            box=settings.QR_POSITION_BOX,
                            W=W, H=H,
                            rot=rotation,
                            anchor=anchor,
                            qr=(qr_w, qr_h),
                            margin=margin,
                            base=(x, y),
                            delta=(0.0, 0.0),  # Будет заполнено при применении эвристик
                            final=(x, y),
                            clamped=True)
            
            return x, y
            
        except Exception as e:
            debug_logger.error("❌ Error computing anchor", 
                            error=str(e), anchor=anchor, rotation=rotation)
            # Fallback к bottom-right
            x = max(0, min(W - margin - qr_w, W - qr_w))
            y = max(0, min(margin, H - qr_h))
            return x, y


# Global PDF service instance - will be created lazily
_pdf_service_instance = None


def get_pdf_service() -> PDFService:
    """Get PDF service instance (lazy initialization)"""
    global _pdf_service_instance
    if _pdf_service_instance is None:
        _pdf_service_instance = PDFService()
    return _pdf_service_instance


# For backward compatibility
pdf_service = get_pdf_service()