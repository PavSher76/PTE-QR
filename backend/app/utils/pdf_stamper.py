"""
PDF stamping utilities for embedding QR codes
"""

import io
from typing import List, Tuple

import structlog
from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import white
from reportlab.pdfgen import canvas

from app.core.config import settings
from app.utils.qr_generator import QRCodeGenerator

logger = structlog.get_logger()


class PDFStamper:
    """PDF stamping utility for embedding QR codes"""

    def __init__(self):
        self.qr_generator = QRCodeGenerator()

    def stamp_pdf_with_qr(
        self,
        pdf_path: str,
        doc_uid: str,
        revision: str,
        pages: List[int],
        position: str = "bottom-right",
        margin_mm: int = 5,
    ) -> bytes:
        """
        Stamp PDF with QR codes on specified pages

        Args:
            pdf_path: Path to input PDF file
            doc_uid: Document UID
            revision: Document revision
            pages: List of page numbers to stamp (1-indexed)
            position: QR position (bottom-right, top-right, top-center)
            margin_mm: Margin from edge in millimeters

        Returns:
            Stamped PDF as bytes
        """
        try:
            # Read input PDF
            with open(pdf_path, "rb") as file:
                pdf_reader = PdfReader(file)
                pdf_writer = PdfWriter()

                # Process each page
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]

                    # Check if this page needs QR stamping
                    if (page_num + 1) in pages:
                        # Generate QR code for this page
                        qr_image = self.qr_generator.generate_qr_for_pdf_stamp(
                            doc_uid, revision, page_num + 1
                        )

                        # Create stamp PDF
                        stamp_pdf = self._create_qr_stamp(
                            qr_image,
                            position,
                            margin_mm,
                            page.mediabox.width,
                            page.mediabox.height,
                        )

                        # Merge stamp with page
                        page.merge_page(stamp_pdf.pages[0])

                    pdf_writer.add_page(page)

                # Write output PDF
                output_buffer = io.BytesIO()
                pdf_writer.write(output_buffer)
                return output_buffer.getvalue()

        except Exception as e:
            logger.error(
                "Failed to stamp PDF",
                pdf_path=pdf_path,
                doc_uid=doc_uid,
                revision=revision,
                error=str(e),
                exc_info=True,
            )
            raise

    def _create_qr_stamp(
        self,
        qr_image: Image.Image,
        position: str,
        margin_mm: int,
        page_width: float,
        page_height: float,
    ) -> PdfWriter:
        """
        Create PDF stamp with QR code

        Args:
            qr_image: QR code PIL Image
            position: Position on page
            margin_mm: Margin in millimeters
            page_width: Page width in points
            page_height: Page height in points

        Returns:
            PDF writer with stamp
        """
        # Convert QR image to bytes
        qr_buffer = io.BytesIO()
        qr_image.save(qr_buffer, format="PNG")
        qr_data = qr_buffer.getvalue()

        # Calculate position
        qr_size_mm = settings.QR_SIZE_MM
        qr_size_points = qr_size_mm * 72 / 25.4  # Convert mm to points
        margin_points = margin_mm * 72 / 25.4

        if position == "bottom-right":
            x = page_width - qr_size_points - margin_points
            y = margin_points
        elif position == "top-right":
            x = page_width - qr_size_points - margin_points
            y = page_height - qr_size_points - margin_points
        elif position == "top-center":
            x = (page_width - qr_size_points) / 2
            y = page_height - qr_size_points - margin_points
        else:
            # Default to bottom-right
            x = page_width - qr_size_points - margin_points
            y = margin_points

        # Create stamp PDF
        stamp_buffer = io.BytesIO()
        stamp_canvas = canvas.Canvas(stamp_buffer, pagesize=(page_width, page_height))

        # Draw white background rectangle
        stamp_canvas.setFillColor(white)
        stamp_canvas.rect(x - 2, y - 2, qr_size_points + 4, qr_size_points + 4, fill=1)

        # Draw QR code
        stamp_canvas.drawImage(
            io.BytesIO(qr_data),
            x,
            y,
            width=qr_size_points,
            height=qr_size_points,
            mask="auto",
        )

        stamp_canvas.save()

        # Create PDF writer
        stamp_buffer.seek(0)
        stamp_reader = PdfReader(stamp_buffer)
        stamp_writer = PdfWriter()
        stamp_writer.add_page(stamp_reader.pages[0])

        return stamp_writer

    def get_stamp_positions(
        self,
        page_width: float,
        page_height: float,
        position: str = "bottom-right",
        margin_mm: int = 5,
    ) -> List[Tuple[float, float]]:
        """
        Get QR stamp positions for all pages

        Args:
            page_width: Page width in points
            page_height: Page height in points
            position: Position on page
            margin_mm: Margin in millimeters

        Returns:
            List of (x, y) positions in points
        """
        qr_size_mm = settings.QR_SIZE_MM
        qr_size_points = qr_size_mm * 72 / 25.4
        margin_points = margin_mm * 72 / 25.4

        if position == "bottom-right":
            x = page_width - qr_size_points - margin_points
            y = margin_points
        elif position == "top-right":
            x = page_width - qr_size_points - margin_points
            y = page_height - qr_size_points - margin_points
        elif position == "top-center":
            x = (page_width - qr_size_points) / 2
            y = page_height - qr_size_points - margin_points
        else:
            x = page_width - qr_size_points - margin_points
            y = margin_points

        return [(x, y)]
