"""
Service for PDF processing and QR code integration
"""

import os
import tempfile
import uuid
from typing import Dict, Any, List
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from io import BytesIO
import structlog

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
            
            # Get page dimensions
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            # QR code size: 3.5 cm x 3.5 cm as per requirements
            # Convert cm to points: 1 cm = 28.35 points
            qr_size_cm = 3.5
            qr_size = qr_size_cm * 28.35  # 99.225 points
            
            # Calculate position based on page orientation and detected elements
            is_landscape = page_width > page_height
            
            if is_landscape:
                # For Landscape pages: Use intelligent positioning
                x_position, y_position = self._calculate_landscape_qr_position(
                    page_width, page_height, qr_size, pdf_path, page_number - 1
                )
                logger.info(f"Landscape page detected - QR positioned intelligently at ({x_position:.1f}, {y_position:.1f})")
            else:
                # For Portrait pages: Skip QR code placement
                logger.info(f"Portrait page detected - skipping QR code placement (portrait pages not supported)")
                return page
            
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
            
            # Get detected positions using new algorithm
            free_space = layout_info.get("free_space_3_5cm")
            horizontal_line = layout_info.get("horizontal_line_18cm")
            right_frame_edge = layout_info.get("right_frame_edge")
            
            debug_logger.info("New algorithm analysis results", 
                            free_space_3_5cm=free_space,
                            horizontal_line_18cm=horizontal_line,
                            right_frame_edge=right_frame_edge)
            
            # Use new algorithm: search for free space 3.5x3.5 cm
            if free_space:
                x_position = free_space["x"]
                y_position = free_space["y"]
                
                debug_logger.info("✅ Using new algorithm - free space 3.5x3.5cm found", 
                                x_position=x_position, y_position=y_position,
                                x_cm=round(x_position / 28.35, 2),
                                y_cm=round(y_position / 28.35, 2))
                
                # Log final QR code positioning with pixel coordinates
                debug_logger.info("Final QR code positioning (new algorithm)",
                                qr_x_position_points=x_position,
                                qr_y_position_points=y_position,
                                qr_x_position_pixels=int(x_position * 2),
                                qr_y_position_pixels=int(y_position * 2),
                                qr_x_position_cm=round(x_position / 28.35, 2),
                                qr_y_position_cm=round(y_position / 28.35, 2),
                                qr_size_points=qr_size,
                                qr_size_pixels=int(qr_size * 2),
                                qr_size_cm=round(qr_size / 28.35, 2))
                
                return x_position, y_position
            
            # Fallback to new fallback algorithm if new algorithm fails
            debug_logger.warning("New algorithm failed, falling back to frame-based algorithm")
            
            # Get frame positions for fallback algorithm
            bottom_frame_edge = layout_info.get("bottom_frame_edge")
            
            debug_logger.info("Fallback algorithm analysis results", 
                            right_frame_edge=right_frame_edge,
                            bottom_frame_edge=bottom_frame_edge)
            
            # Log detailed positioning information
            debug_logger.info("QR positioning details - page dimensions and element positions",
                            page_width_points=page_width,
                            page_height_points=page_height,
                            page_width_pixels=int(page_width * 2),  # Assuming 2x scale factor
                            page_height_pixels=int(page_height * 2),  # Assuming 2x scale factor
                            right_frame_edge_points=right_frame_edge,
                            right_frame_edge_pixels=int(right_frame_edge * 2) if right_frame_edge else None,
                            bottom_frame_edge_points=bottom_frame_edge,
                            bottom_frame_edge_pixels=int(bottom_frame_edge * 2) if bottom_frame_edge else None,
                            qr_size_points=qr_size,
                            qr_size_pixels=int(qr_size * 2))
            
            # FALLBACK 1: Position along bottom and right frame edges
            if bottom_frame_edge is not None and right_frame_edge is not None:
                debug_logger.info("Using FALLBACK 1: Position along bottom and right frame edges")
                
                # Y position: above bottom frame with margin
                margin_cm = 0.5  # 0.5 cm margin above bottom frame
                margin_points = margin_cm * 28.35
                y_position = bottom_frame_edge + margin_points
                
                # X position: left of right frame with margin
                x_position = right_frame_edge - qr_size - margin_points
                
                # Ensure QR code doesn't go off the page
                max_y = page_height - qr_size - (1.0 * 28.35)  # 1 cm from top
                y_position = min(y_position, max_y)
                
                min_x = 1.0 * 28.35  # 1 cm from left edge
                x_position = max(x_position, min_x)
                
                debug_logger.info("FALLBACK 1 positioning", 
                                bottom_frame_edge=bottom_frame_edge,
                                right_frame_edge=right_frame_edge,
                                x_position=x_position,
                                y_position=y_position,
                                margin_cm=margin_cm)
                
            elif right_frame_edge is not None:
                debug_logger.info("Using FALLBACK 1 (right frame only): Position along right frame edge")
                
                # Y position: use default (bottom area)
                y_position = default_y
                
                # X position: left of right frame with margin
                margin_cm = 0.5  # 0.5 cm margin from right frame
                margin_points = margin_cm * 28.35
                x_position = right_frame_edge - qr_size - margin_points
                
                # Ensure QR code doesn't go off the left edge
                min_x = 1.0 * 28.35  # 1 cm from left edge
                x_position = max(x_position, min_x)
                
                debug_logger.info("FALLBACK 1 (right frame only) positioning", 
                                right_frame_edge=right_frame_edge,
                                x_position=x_position,
                                y_position=y_position,
                                margin_cm=margin_cm)
                
            elif bottom_frame_edge is not None:
                debug_logger.info("Using FALLBACK 1 (bottom frame only): Position along bottom frame edge")
                
                # Y position: above bottom frame with margin
                margin_cm = 0.5  # 0.5 cm margin above bottom frame
                margin_points = margin_cm * 28.35
                y_position = bottom_frame_edge + margin_points
                
                # X position: use default (left area)
                x_position = default_x
                
                # Ensure QR code doesn't go off the top of the page
                max_y = page_height - qr_size - (1.0 * 28.35)  # 1 cm from top
                y_position = min(y_position, max_y)
                
                debug_logger.info("FALLBACK 1 (bottom frame only) positioning", 
                                bottom_frame_edge=bottom_frame_edge,
                                x_position=x_position,
                                y_position=y_position,
                                margin_cm=margin_cm)
                
            else:
                # FALLBACK 2: 1 cm offset from bottom-right corner of the page
                debug_logger.info("Using FALLBACK 2: 1 cm offset from bottom-right corner")
                
                margin_cm = 1.0  # 1 cm margin from edges
                margin_points = margin_cm * 28.35
                
                # Position QR code 1 cm from bottom-right corner
                x_position = page_width - qr_size - margin_points
                y_position = margin_points
                
                debug_logger.info("FALLBACK 2 positioning", 
                                page_width=page_width,
                                page_height=page_height,
                                x_position=x_position,
                                y_position=y_position,
                                margin_cm=margin_cm)
            
            debug_logger.info("Calculated QR position (fallback algorithm)", 
                            x_position=x_position, y_position=y_position,
                            right_frame_edge=right_frame_edge, bottom_frame_edge=bottom_frame_edge)
            
            # Log final QR code positioning with pixel coordinates
            debug_logger.info("Final QR code positioning (fallback algorithm)",
                            qr_x_position_points=x_position,
                            qr_y_position_points=y_position,
                            qr_x_position_pixels=int(x_position * 2),
                            qr_y_position_pixels=int(y_position * 2),
                            qr_x_position_cm=round(x_position / 28.35, 2),
                            qr_y_position_cm=round(y_position / 28.35, 2),
                            qr_size_points=qr_size,
                            qr_size_pixels=int(qr_size * 2),
                            qr_size_cm=round(qr_size / 28.35, 2))
            
            return x_position, y_position
            
        except Exception as e:
            debug_logger.error("Error calculating landscape QR position", 
                             error=str(e), pdf_path=pdf_path, page_number=page_number)
            # Return default position on error
            return default_x, default_y

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
                # Get actual page dimensions from the PDF page
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
                from copy import deepcopy
                modified_page = deepcopy(page)
                
                # Convert PIL Image to ReportLab Image
                from PIL import Image
                pil_image = Image.open(BytesIO(qr_image_bytes))
                
                if is_landscape:
                    # For Landscape pages: Use intelligent positioning with PDF analysis
                    logger.info(f"Landscape page detected - using intelligent positioning with PDF analysis")
                    
                    # Save PDF content to temporary file for analysis
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                        temp_pdf.write(pdf_content)
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
                        import os
                        if os.path.exists(temp_pdf_path):
                            os.unlink(temp_pdf_path)
                    
                    logger.info(f"QR positioning details: page_size=({page_width:.1f}x{page_height:.1f}), qr_size={qr_size_points:.1f}, position=({x_position:.1f}, {y_position:.1f})")

                # Save PIL image to temporary file for ReportLab
                import tempfile
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
                    import os
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