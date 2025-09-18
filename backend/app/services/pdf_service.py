"""
PDF processing service
"""

import io
from typing import Any, Dict, List, Optional, Tuple

import pypdf
import structlog
from PIL import Image
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.core.config import settings
from app.services.qr_service import qr_service

logger = structlog.get_logger()


class PDFStamper:
    """PDF stamping service"""

    def __init__(self):
        self.qr_size_mm = settings.PDF_QR_SIZE
        self.qr_position = settings.PDF_QR_POSITION

    def stamp_pdf_with_qr(
        self,
        pdf_data: bytes,
        doc_uid: str,
        revision: str,
        pages: List[int],
        dpi: int = 300,
    ) -> bytes:
        """Stamp PDF with QR codes"""
        try:
            # Read input PDF
            input_pdf = pypdf.PdfReader(io.BytesIO(pdf_data))
            output_pdf = pypdf.PdfWriter()

            # Process each page
            for page_num in range(len(input_pdf.pages)):
                page = input_pdf.pages[page_num]

                # Check if this page needs QR code
                if (page_num + 1) in pages:
                    # Generate QR code for this page
                    qr_img = qr_service.generate_qr_for_pdf_stamp(
                        doc_uid, revision, page_num + 1, dpi, self.qr_size_mm
                    )

                    # Create stamp PDF
                    stamp_pdf = self._create_qr_stamp_pdf(
                        qr_img, page.mediabox.width, page.mediabox.height, dpi
                    )

                    # Merge stamp with page
                    page.merge_page(stamp_pdf.pages[0])

                output_pdf.add_page(page)

            # Write output PDF
            output_buffer = io.BytesIO()
            output_pdf.write(output_buffer)
            return output_buffer.getvalue()

        except Exception as e:
            logger.error(
                "Failed to stamp PDF with QR codes",
                doc_uid=doc_uid,
                revision=revision,
                pages=pages,
                error=str(e),
            )
            raise

    def _create_qr_stamp_pdf(
        self, qr_img: Image.Image, page_width: float, page_height: float, dpi: int
    ) -> pypdf.PdfWriter:
        """Create PDF with QR code stamp"""
        try:
            # Convert QR image to bytes
            qr_buffer = io.BytesIO()
            qr_img.save(qr_buffer, format="PNG")
            qr_buffer.seek(0)

            # Create stamp PDF
            stamp_buffer = io.BytesIO()
            c = canvas.Canvas(stamp_buffer, pagesize=(page_width, page_height))

            # Calculate position
            qr_width_pt = self.qr_size_mm * mm
            qr_height_pt = self.qr_size_mm * mm

            if self.qr_position == "bottom-right":
                x = page_width - qr_width_pt - 10
                y = 10
            elif self.qr_position == "bottom-left":
                x = 10
                y = 10
            elif self.qr_position == "top-right":
                x = page_width - qr_width_pt - 10
                y = page_height - qr_height_pt - 10
            elif self.qr_position == "top-left":
                x = 10
                y = page_height - qr_height_pt - 10
            else:  # center
                x = (page_width - qr_width_pt) / 2
                y = (page_height - qr_height_pt) / 2

            # Draw QR code
            c.drawImage(
                qr_buffer, x, y, width=qr_width_pt, height=qr_height_pt, mask="auto"
            )

            c.save()
            stamp_buffer.seek(0)

            # Convert to PyPDF2
            stamp_pdf = pypdf.PdfReader(stamp_buffer)
            return stamp_pdf

        except Exception as e:
            logger.error("Failed to create QR stamp PDF", error=str(e))
            raise

    def extract_pdf_info(self, pdf_data: bytes) -> Dict[str, Any]:
        """Extract information from PDF"""
        try:
            pdf_reader = pypdf.PdfReader(io.BytesIO(pdf_data))

            info = {
                "pages": len(pdf_reader.pages),
                "title": (
                    pdf_reader.metadata.get("/Title", "") if pdf_reader.metadata else ""
                ),
                "author": (
                    pdf_reader.metadata.get("/Author", "")
                    if pdf_reader.metadata
                    else ""
                ),
                "subject": (
                    pdf_reader.metadata.get("/Subject", "")
                    if pdf_reader.metadata
                    else ""
                ),
                "creator": (
                    pdf_reader.metadata.get("/Creator", "")
                    if pdf_reader.metadata
                    else ""
                ),
                "producer": (
                    pdf_reader.metadata.get("/Producer", "")
                    if pdf_reader.metadata
                    else ""
                ),
                "creation_date": (
                    pdf_reader.metadata.get("/CreationDate", "")
                    if pdf_reader.metadata
                    else ""
                ),
                "modification_date": (
                    pdf_reader.metadata.get("/ModDate", "")
                    if pdf_reader.metadata
                    else ""
                ),
            }

            return info

        except Exception as e:
            logger.error("Failed to extract PDF info", error=str(e))
            raise

    def validate_pdf(self, pdf_data: bytes) -> Tuple[bool, Optional[str]]:
        """Validate PDF file"""
        try:
            pdf_reader = pypdf.PdfReader(io.BytesIO(pdf_data))

            # Check if PDF is encrypted
            if pdf_reader.is_encrypted:
                return False, "PDF is encrypted"

            # Check number of pages
            if len(pdf_reader.pages) == 0:
                return False, "PDF has no pages"

            # Check if PDF is too large
            if len(pdf_data) > settings.MAX_FILE_SIZE:
                return False, f"PDF is too large (max {settings.MAX_FILE_SIZE} bytes)"

            return True, None

        except Exception as e:
            logger.error("PDF validation failed", error=str(e))
            return False, f"Invalid PDF: {str(e)}"

    def create_pdf_with_qr_codes(
        self,
        doc_uid: str,
        revision: str,
        pages: List[int],
        title: str = "",
        dpi: int = 300,
    ) -> bytes:
        """Create new PDF with QR codes"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas

            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)

            for page_num in pages:
                # Generate QR code
                qr_img = qr_service.generate_qr_for_pdf_stamp(
                    doc_uid, revision, page_num, dpi, self.qr_size_mm
                )

                # Convert to bytes
                qr_buffer = io.BytesIO()
                qr_img.save(qr_buffer, format="PNG")
                qr_buffer.seek(0)

                # Add page title
                if title:
                    c.setFont("Helvetica-Bold", 16)
                    c.drawString(50, A4[1] - 50, f"{title} - Page {page_num}")

                # Add QR code
                qr_size_pt = self.qr_size_mm * mm
                c.drawImage(
                    qr_buffer,
                    50,
                    A4[1] - 100,
                    width=qr_size_pt,
                    height=qr_size_pt,
                    mask="auto",
                )

                # Add document info
                c.setFont("Helvetica", 10)
                c.drawString(50, A4[1] - 120, f"Document: {doc_uid}")
                c.drawString(50, A4[1] - 135, f"Revision: {revision}")
                c.drawString(50, A4[1] - 150, f"Page: {page_num}")

                c.showPage()

            c.save()
            buffer.seek(0)
            return buffer.getvalue()

        except Exception as e:
            logger.error(
                "Failed to create PDF with QR codes",
                doc_uid=doc_uid,
                revision=revision,
                pages=pages,
                error=str(e),
            )
            raise


# Global PDF service instance
pdf_service = PDFStamper()
