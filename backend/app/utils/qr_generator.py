"""
QR Code generation utilities
"""

import base64
from io import BytesIO
from typing import Any, Dict, List

import qrcode
import segno
import structlog
from PIL import Image, ImageDraw, ImageFont

from app.core.config import settings
from app.models.qr_code import QRCodeFormatEnum, QRCodeStyleEnum
from app.utils.hmac_signer import HMACSigner

logger = structlog.get_logger()


class QRCodeGenerator:
    """QR Code generation with various formats and styles"""

    def __init__(self):
        self.hmac_signer = HMACSigner()

    def generate_qr_codes(
        self,
        doc_uid: str,
        revision: str,
        pages: List[int],
        style: QRCodeStyleEnum = QRCodeStyleEnum.BLACK,
        dpi: int = 300,
        size_mm: int = 35,
    ) -> List[Dict[str, Any]]:
        """
        Generate QR codes for multiple pages

        Args:
            doc_uid: Document UID
            revision: Document revision
            pages: List of page numbers
            style: QR code style
            dpi: DPI for generation
            size_mm: Size in millimeters

        Returns:
            List of QR code data dictionaries
        """
        results = []

        for page in pages:
            try:
                # Generate QR URL with signature
                qr_url = self.hmac_signer.generate_qr_url(doc_uid, revision, page)

                # Generate QR code image
                qr_data = self._generate_qr_image(qr_url, style, dpi, size_mm)

                results.append({"page": page, "url": qr_url, "data": qr_data})

                logger.info(
                    "QR code generated",
                    doc_uid=doc_uid,
                    revision=revision,
                    page=page,
                    style=style.value,
                )

            except Exception as e:
                logger.error(
                    "Failed to generate QR code",
                    doc_uid=doc_uid,
                    revision=revision,
                    page=page,
                    error=str(e),
                    exc_info=True,
                )
                raise

        return results

    def _generate_qr_image(
        self, url: str, style: QRCodeStyleEnum, dpi: int, size_mm: int
    ) -> Dict[str, str]:
        """
        Generate QR code image in multiple formats

        Args:
            url: URL to encode in QR
            style: QR code style
            dpi: DPI for generation
            size_mm: Size in millimeters

        Returns:
            Dictionary with base64 encoded images
        """
        # Calculate size in pixels
        size_px = int(size_mm * dpi / 25.4)  # Convert mm to pixels

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # Create QR code image in RGB mode
        qr_image = qr.make_image(fill_color="black", back_color="white")
        # Convert to RGB to ensure compatibility
        if qr_image.mode != "RGB":
            qr_image = qr_image.convert("RGB")

        # Resize to target size
        qr_image = qr_image.resize((size_px, size_px), Image.Resampling.LANCZOS)

        # Apply style
        styled_image = self._apply_style(qr_image, style, size_px)

        # Convert to different formats
        result = {}

        # PNG format - ensure RGB mode
        png_buffer = BytesIO()
        if styled_image.mode != "RGB":
            styled_image = styled_image.convert("RGB")
        styled_image.save(png_buffer, format="PNG", dpi=(dpi, dpi))
        result["png"] = base64.b64encode(png_buffer.getvalue()).decode("utf-8")

        # SVG format (using segno for better SVG support)
        svg_buffer = BytesIO()
        segno_qr = segno.make(url, error="M")
        segno_qr.save(svg_buffer, kind="svg", scale=10)
        result["svg"] = base64.b64encode(svg_buffer.getvalue()).decode("utf-8")

        return result

    def _apply_style(
        self, image: Image.Image, style: QRCodeStyleEnum, size_px: int
    ) -> Image.Image:
        """
        Apply style to QR code image

        Args:
            image: Base QR code image
            style: Style to apply
            size_px: Image size in pixels

        Returns:
            Styled QR code image
        """
        if style == QRCodeStyleEnum.BLACK:
            return image

        elif style == QRCodeStyleEnum.INVERTED:
            # Invert colors
            inverted = Image.new("RGB", image.size, "black")
            inverted.paste(image, (0, 0))
            return inverted

        elif style == QRCodeStyleEnum.WITH_LABEL:
            # Add label below QR code
            label_height = 30
            total_height = size_px + label_height

            # Create new image with space for label
            labeled_image = Image.new("RGB", (size_px, total_height), "white")
            labeled_image.paste(image, (0, 0))

            # Add label
            draw = ImageDraw.Draw(labeled_image)
            try:
                # Try to use a system font
                font = ImageFont.truetype("arial.ttf", 12)
            except OSError:
                # Fallback to default font
                font = ImageFont.load_default()

            # Calculate text position (centered)
            text = "PTI QR"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = (size_px - text_width) // 2
            text_y = size_px + 5

            draw.text((text_x, text_y), text, fill="black", font=font)

            return labeled_image

        return image

    def generate_qr_for_pdf_stamp(
        self, doc_uid: str, revision: str, page: int, dpi: int = 300, size_mm: int = 35
    ) -> Image.Image:
        """
        Generate QR code image specifically for PDF stamping

        Args:
            doc_uid: Document UID
            revision: Document revision
            page: Page number
            dpi: DPI for generation
            size_mm: Size in millimeters

        Returns:
            PIL Image ready for PDF stamping
        """
        qr_url = self.hmac_signer.generate_qr_url(doc_uid, revision, page)
        qr_data = self._generate_qr_image(qr_url, QRCodeStyleEnum.BLACK, dpi, size_mm)

        # Return PNG image in RGB mode
        png_data = base64.b64decode(qr_data["png"])
        image = Image.open(BytesIO(png_data))
        # Ensure RGB mode for compatibility
        if image.mode != "RGB":
            image = image.convert("RGB")
        return image
