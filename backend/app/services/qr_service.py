"""
QR Code generation service
"""

import base64
import io
from typing import Any, Dict, List, Optional

import qrcode
import segno
import structlog
from PIL import Image, ImageDraw, ImageFont

from app.core.config import settings
from app.utils.hmac_signer import HMACSigner

logger = structlog.get_logger()


class QRCodeGenerator:
    """QR Code generator service"""

    def __init__(self):
        self.hmac_signer = HMACSigner()
        self.base_url = "https://pte-qr.pti.ru"

    def _generate_qr_url(self, doc_uid: str, revision: str, page: int) -> str:
        """Generate QR code URL with HMAC signature"""
        return self.hmac_signer.generate_qr_url(doc_uid, revision, page)

    def _create_qr_image(
        self,
        data: str,
        size: int = 200,
        border: int = 4,
        error_correction: str = "M",
        style: str = "BLACK",
    ) -> Image.Image:
        """Create QR code image"""
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=getattr(
                qrcode.constants, f"ERROR_CORRECT_{error_correction}"
            ),
            box_size=size // 25,  # Adjust box size based on total size
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Create image
        if style == "BLACK":
            fill_color = "black"
            back_color = "white"
        elif style == "INVERTED":
            fill_color = "white"
            back_color = "black"
        else:
            fill_color = "black"
            back_color = "white"

        img = qr.make_image(fill_color=fill_color, back_color=back_color)

        # Resize to exact size
        img = img.resize((size, size), Image.Resampling.LANCZOS)

        return img

    def _create_qr_with_label(
        self,
        data: str,
        label: str,
        size: int = 200,
        border: int = 4,
        error_correction: str = "M",
    ) -> Image.Image:
        """Create QR code with label"""
        # Create base QR code
        qr_img = self._create_qr_image(data, size - 40, border, error_correction)

        # Create image with space for label
        final_img = Image.new("RGB", (size, size + 30), "white")

        # Paste QR code
        final_img.paste(qr_img, (20, 0))

        # Add label
        try:
            draw = ImageDraw.Draw(final_img)
            # Try to use a system font
            try:
                font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12
                )
            except:
                font = ImageFont.load_default()

            # Center the text
            bbox = draw.textbbox((0, 0), label, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = (size - text_width) // 2

            draw.text((text_x, size - 25), label, fill="black", font=font)
        except Exception as e:
            logger.warning("Failed to add label to QR code", error=str(e))

        return final_img

    def generate_qr_codes(
        self,
        doc_uid: str,
        revision: str,
        pages: List[int],
        style: str = "BLACK",
        dpi: int = 300,
        size: int = 200,
    ) -> List[Dict[str, Any]]:
        """Generate QR codes for multiple pages"""
        results = []

        for page in pages:
            try:
                # Generate URL
                qr_url = self._generate_qr_url(doc_uid, revision, page)

                # Create QR code image
                if style == "WITH_LABEL":
                    qr_img = self._create_qr_with_label(
                        qr_url, f"{doc_uid} Rev.{revision} P.{page}", size
                    )
                else:
                    qr_img = self._create_qr_image(qr_url, size, style=style)

                # Convert to different formats
                png_data = self._image_to_base64(qr_img, "PNG")
                svg_data = self._generate_svg_qr(qr_url, size)

                results.append(
                    {
                        "page": page,
                        "url": qr_url,
                        "data": {"png": png_data, "svg": svg_data},
                    }
                )

                logger.info(
                    "QR code generated",
                    doc_uid=doc_uid,
                    revision=revision,
                    page=page,
                    style=style,
                )

            except Exception as e:
                logger.error(
                    "Failed to generate QR code",
                    doc_uid=doc_uid,
                    revision=revision,
                    page=page,
                    error=str(e),
                )
                raise

        return results

    def generate_qr_for_pdf_stamp(
        self, doc_uid: str, revision: str, page: int, dpi: int = 300, size_mm: int = 35
    ) -> Image.Image:
        """Generate QR code optimized for PDF stamping"""
        # Convert mm to pixels (assuming 300 DPI)
        size_px = int(size_mm * dpi / 25.4)

        # Generate URL
        qr_url = self._generate_qr_url(doc_uid, revision, page)

        # Create QR code with high error correction for small size
        qr = segno.make(qr_url, error="h")  # High error correction

        # Convert to PIL Image
        qr_img = qr.to_pil(size=size_px, border=2)

        # Convert to RGB if needed
        if qr_img.mode != "RGB":
            qr_img = qr_img.convert("RGB")

        return qr_img

    def _image_to_base64(self, img: Image.Image, format: str) -> str:
        """Convert PIL Image to base64 string"""
        buffer = io.BytesIO()
        img.save(buffer, format=format)
        return base64.b64encode(buffer.getvalue()).decode()

    def _generate_svg_qr(self, data: str, size: int) -> str:
        """Generate SVG QR code"""
        qr = segno.make(data)
        return qr.svg_inline(scale=size // 25, border=2)

    def verify_qr_signature(
        self, doc_uid: str, revision: str, page: int, timestamp: int, signature: str
    ) -> bool:
        """Verify QR code signature"""
        return self.hmac_signer.verify_signature(
            doc_uid, revision, page, timestamp, signature
        )


# Global QR service instance
qr_service = QRCodeGenerator()
