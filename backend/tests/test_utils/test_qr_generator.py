"""
Unit tests for QR code generator utility
"""

import base64

from PIL import Image

from app.models.qr_code import QRCodeStyleEnum
from app.utils.qr_generator import QRCodeGenerator


class TestQRCodeGenerator:
    """Test QR code generator functionality"""

    def setup_method(self):
        """Set up test fixtures."""
        self.generator = QRCodeGenerator()
        self.doc_uid = "TEST-DOC-001"
        self.revision = "A"
        self.pages = [1, 2, 3]

    def test_generate_qr_codes(self):
        """Test QR code generation for multiple pages."""
        results = self.generator.generate_qr_codes(
            doc_uid=self.doc_uid,
            revision=self.revision,
            pages=self.pages,
            style=QRCodeStyleEnum.BLACK,
            dpi=300,
            size_mm=35,
        )

        assert len(results) == len(self.pages)

        for i, result in enumerate(results):
            assert result["page"] == self.pages[i]
            assert "url" in result
            assert "data" in result
            assert "png" in result["data"]
            assert "svg" in result["data"]

            # Verify PNG data is valid base64
            png_data = result["data"]["png"]
            decoded_png = base64.b64decode(png_data)
            assert len(decoded_png) > 0

            # Verify SVG data is valid base64
            svg_data = result["data"]["svg"]
            decoded_svg = base64.b64decode(svg_data)
            assert len(decoded_svg) > 0

    def test_generate_qr_codes_different_styles(self):
        """Test QR code generation with different styles."""
        styles = [
            QRCodeStyleEnum.BLACK,
            QRCodeStyleEnum.INVERTED,
            QRCodeStyleEnum.WITH_LABEL,
        ]

        for style in styles:
            results = self.generator.generate_qr_codes(
                doc_uid=self.doc_uid,
                revision=self.revision,
                pages=[1],
                style=style,
                dpi=300,
                size_mm=35,
            )

            assert len(results) == 1
            assert "data" in results[0]
            assert "png" in results[0]["data"]

    def test_generate_qr_codes_different_sizes(self):
        """Test QR code generation with different sizes."""
        sizes = [25, 35, 50]

        for size in sizes:
            results = self.generator.generate_qr_codes(
                doc_uid=self.doc_uid,
                revision=self.revision,
                pages=[1],
                style=QRCodeStyleEnum.BLACK,
                dpi=300,
                size_mm=size,
            )

            assert len(results) == 1
            assert "data" in results[0]

    def test_generate_qr_for_pdf_stamp(self):
        """Test QR code generation for PDF stamping."""
        qr_image = self.generator.generate_qr_for_pdf_stamp(
            doc_uid=self.doc_uid, revision=self.revision, page=1, dpi=300, size_mm=35
        )

        assert qr_image is not None
        assert isinstance(qr_image, Image.Image)
        assert qr_image.mode in ["RGB", "RGBA", "L", "1"]

    def test_qr_url_contains_correct_parameters(self):
        """Test that generated QR URLs contain correct parameters."""
        results = self.generator.generate_qr_codes(
            doc_uid=self.doc_uid,
            revision=self.revision,
            pages=[1],
            style=QRCodeStyleEnum.BLACK,
        )

        url = results[0]["url"]
        assert self.doc_uid in url
        assert self.revision in url
        assert "1" in url  # page number
        assert "t=" in url  # signature parameter
        assert "ts=" in url  # timestamp parameter

    def test_generate_qr_codes_empty_pages(self):
        """Test QR code generation with empty pages list."""
        results = self.generator.generate_qr_codes(
            doc_uid=self.doc_uid,
            revision=self.revision,
            pages=[],
            style=QRCodeStyleEnum.BLACK,
        )

        assert len(results) == 0

    def test_generate_qr_codes_single_page(self):
        """Test QR code generation for single page."""
        results = self.generator.generate_qr_codes(
            doc_uid=self.doc_uid,
            revision=self.revision,
            pages=[1],
            style=QRCodeStyleEnum.BLACK,
        )

        assert len(results) == 1
        assert results[0]["page"] == 1

    def test_generate_qr_codes_large_page_numbers(self):
        """Test QR code generation with large page numbers."""
        large_pages = [100, 200, 300]

        results = self.generator.generate_qr_codes(
            doc_uid=self.doc_uid,
            revision=self.revision,
            pages=large_pages,
            style=QRCodeStyleEnum.BLACK,
        )

        assert len(results) == len(large_pages)
        for i, result in enumerate(results):
            assert result["page"] == large_pages[i]

    def test_generate_qr_codes_special_characters(self):
        """Test QR code generation with special characters in document info."""
        special_doc_uid = "TEST-DOC-001@#$%"
        special_revision = "A-1.0"

        results = self.generator.generate_qr_codes(
            doc_uid=special_doc_uid,
            revision=special_revision,
            pages=[1],
            style=QRCodeStyleEnum.BLACK,
        )

        assert len(results) == 1
        url = results[0]["url"]
        assert special_doc_uid in url
        assert special_revision in url
