"""
PDF stamping service
"""

import asyncio
import tempfile
import os
from typing import List, Dict, Any, Optional, BinaryIO
from datetime import datetime
import structlog

from app.core.config import settings
from app.utils.pdf_stamper import PDFStamper
from app.services.qr_service import qr_service
from app.core.cache import cache_manager
from app.core.database import get_db
from app.models.user import User

logger = structlog.get_logger()


class PDFStampingService:
    """PDF stamping service for embedding QR codes"""
    
    def __init__(self):
        self.stamper = PDFStamper()
        self.cache_ttl = 3600  # 1 hour for stamped PDFs
    
    async def stamp_pdf_with_qr_codes(
        self,
        pdf_file: BinaryIO,
        doc_uid: str,
        revision: str,
        pages: List[int],
        position: str = "bottom-right",
        margin_mm: int = 5,
        user: Optional[User] = None
    ) -> bytes:
        """
        Stamp PDF with QR codes on specified pages
        
        Args:
            pdf_file: PDF file as binary stream
            doc_uid: Document UID
            revision: Document revision
            pages: List of page numbers to stamp (1-indexed)
            position: QR position (bottom-right, top-right, top-center)
            margin_mm: Margin from edge in millimeters
            user: User performing the stamping
            
        Returns:
            Stamped PDF as bytes
        """
        try:
            # Check cache for existing stamped PDF
            cache_key = f"stamped_pdf:{doc_uid}:{revision}:{position}:{margin_mm}:{','.join(map(str, pages))}"
            cached_pdf = await cache_manager.get(cache_key)
            if cached_pdf:
                logger.info("Stamped PDF retrieved from cache", doc_uid=doc_uid, revision=revision, pages=pages)
                return cached_pdf
            
            # Create temporary file for input PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_input:
                temp_input.write(pdf_file.read())
                temp_input_path = temp_input.name
            
            try:
                # Stamp PDF with QR codes
                stamped_pdf_bytes = self.stamper.stamp_pdf_with_qr(
                    pdf_path=temp_input_path,
                    doc_uid=doc_uid,
                    revision=revision,
                    pages=pages,
                    position=position,
                    margin_mm=margin_mm
                )
                
                # Cache the result
                await cache_manager.set(cache_key, stamped_pdf_bytes, ttl=self.cache_ttl)
                
                # Log the stamping operation
                await self._log_pdf_stamping(
                    doc_uid=doc_uid,
                    revision=revision,
                    pages=pages,
                    position=position,
                    user=user
                )
                
                logger.info(
                    "PDF stamped successfully",
                    doc_uid=doc_uid,
                    revision=revision,
                    pages=pages,
                    position=position
                )
                
                return stamped_pdf_bytes
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_input_path):
                    os.unlink(temp_input_path)
                
        except Exception as e:
            logger.error(
                "Failed to stamp PDF",
                doc_uid=doc_uid,
                revision=revision,
                pages=pages,
                error=str(e),
                exc_info=True
            )
            raise
    
    async def generate_pdf_with_qr_codes(
        self,
        doc_uid: str,
        revision: str,
        pages: List[int],
        position: str = "bottom-right",
        margin_mm: int = 5,
        user: Optional[User] = None
    ) -> bytes:
        """
        Generate a new PDF with embedded QR codes (without existing PDF)
        
        Args:
            doc_uid: Document UID
            revision: Document revision
            pages: List of page numbers
            position: QR position
            margin_mm: Margin from edge in millimeters
            user: User generating the PDF
            
        Returns:
            Generated PDF with QR codes as bytes
        """
        try:
            # Check cache
            cache_key = f"generated_pdf:{doc_uid}:{revision}:{position}:{margin_mm}:{','.join(map(str, pages))}"
            cached_pdf = await cache_manager.get(cache_key)
            if cached_pdf:
                logger.info("Generated PDF retrieved from cache", doc_uid=doc_uid, revision=revision, pages=pages)
                return cached_pdf
            
            # Generate QR codes for all pages
            qr_results = await qr_service.generate_qr_codes(
                doc_uid=doc_uid,
                revision=revision,
                pages=pages,
                user=user
            )
            
            # Create PDF with QR codes
            pdf_bytes = self._create_pdf_with_qr_codes(
                qr_results=qr_results,
                doc_uid=doc_uid,
                revision=revision,
                position=position,
                margin_mm=margin_mm
            )
            
            # Cache the result
            await cache_manager.set(cache_key, pdf_bytes, ttl=self.cache_ttl)
            
            # Log the generation
            await self._log_pdf_stamping(
                doc_uid=doc_uid,
                revision=revision,
                pages=pages,
                position=position,
                user=user
            )
            
            logger.info(
                "PDF with QR codes generated successfully",
                doc_uid=doc_uid,
                revision=revision,
                pages=pages
            )
            
            return pdf_bytes
            
        except Exception as e:
            logger.error(
                "Failed to generate PDF with QR codes",
                doc_uid=doc_uid,
                revision=revision,
                pages=pages,
                error=str(e),
                exc_info=True
            )
            raise
    
    def _create_pdf_with_qr_codes(
        self,
        qr_results: Dict[str, Any],
        doc_uid: str,
        revision: str,
        position: str,
        margin_mm: int
    ) -> bytes:
        """
        Create a new PDF with QR codes embedded
        
        Args:
            qr_results: QR code generation results
            doc_uid: Document UID
            revision: Document revision
            position: QR position
            margin_mm: Margin from edge
            
        Returns:
            PDF bytes
        """
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        import base64
        import io
        
        # Create PDF buffer
        pdf_buffer = io.BytesIO()
        pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=A4)
        
        page_width, page_height = A4
        
        for item in qr_results["items"]:
            # Decode QR code image
            qr_image_data = base64.b64decode(item["data_base64"])
            qr_image = io.BytesIO(qr_image_data)
            
            # Calculate position
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
            
            # Add QR code to page
            pdf_canvas.drawImage(
                qr_image,
                x, y,
                width=qr_size_points,
                height=qr_size_points,
                mask='auto'
            )
            
            # Add page info
            pdf_canvas.setFont("Helvetica", 10)
            pdf_canvas.drawString(
                margin_points,
                page_height - 20,
                f"Document: {doc_uid} | Revision: {revision} | Page: {item['page']}"
            )
            
            # Start new page (except for last item)
            if item != qr_results["items"][-1]:
                pdf_canvas.showPage()
        
        pdf_canvas.save()
        pdf_buffer.seek(0)
        
        return pdf_buffer.getvalue()
    
    async def get_stamp_positions(
        self,
        page_width: float,
        page_height: float,
        position: str = "bottom-right",
        margin_mm: int = 5
    ) -> List[Dict[str, float]]:
        """
        Get QR stamp positions for pages
        
        Args:
            page_width: Page width in points
            page_height: Page height in points
            position: Position on page
            margin_mm: Margin in millimeters
            
        Returns:
            List of position dictionaries
        """
        try:
            positions = self.stamper.get_stamp_positions(
                page_width=page_width,
                page_height=page_height,
                position=position,
                margin_mm=margin_mm
            )
            
            return [
                {"x": pos[0], "y": pos[1]}
                for pos in positions
            ]
            
        except Exception as e:
            logger.error(
                "Failed to get stamp positions",
                page_width=page_width,
                page_height=page_height,
                position=position,
                error=str(e)
            )
            return []
    
    async def _log_pdf_stamping(
        self,
        doc_uid: str,
        revision: str,
        pages: List[int],
        position: str,
        user: Optional[User] = None
    ):
        """Log PDF stamping operation to database"""
        try:
            db = next(get_db())
            
            # This would log to a PDF stamping log table
            # For now, we'll just log the operation
            logger.info(
                "PDF stamping logged",
                doc_uid=doc_uid,
                revision=revision,
                pages=pages,
                position=position,
                user_id=user.id if user else None
            )
            
        except Exception as e:
            logger.error(
                "Failed to log PDF stamping",
                doc_uid=doc_uid,
                revision=revision,
                pages=pages,
                error=str(e)
            )
    
    async def invalidate_pdf_cache(self, doc_uid: str, revision: Optional[str] = None):
        """
        Invalidate PDF cache
        
        Args:
            doc_uid: Document UID
            revision: Optional revision to invalidate
        """
        try:
            if revision:
                patterns = [
                    f"stamped_pdf:{doc_uid}:{revision}:*",
                    f"generated_pdf:{doc_uid}:{revision}:*"
                ]
            else:
                patterns = [
                    f"stamped_pdf:{doc_uid}:*",
                    f"generated_pdf:{doc_uid}:*"
                ]
            
            total_deleted = 0
            for pattern in patterns:
                deleted_count = await cache_manager.delete_pattern(pattern)
                total_deleted += deleted_count
            
            logger.info(
                "PDF cache invalidated",
                doc_uid=doc_uid,
                revision=revision,
                deleted_keys=total_deleted
            )
            
        except Exception as e:
            logger.error(
                "Failed to invalidate PDF cache",
                doc_uid=doc_uid,
                revision=revision,
                error=str(e)
            )


# Global service instance
pdf_service = PDFStampingService()
