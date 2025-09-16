"""
QR Code generation service
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import structlog

from app.core.config import settings
from app.utils.qr_generator import QRCodeGenerator
from app.utils.hmac_signer import HMACSigner
from app.models.qr_code import QRCodeFormatEnum, QRCodeStyleEnum
from app.core.cache import cache_manager
from app.core.database import get_db
from app.models.qr_code import QRCode as QRCodeModel
from app.models.user import User

logger = structlog.get_logger()


class QRCodeService:
    """QR Code generation and management service"""
    
    def __init__(self):
        self.generator = QRCodeGenerator()
        self.hmac_signer = HMACSigner()
        self.cache_ttl = 3600  # 1 hour for QR codes
    
    async def generate_qr_codes(
        self,
        doc_uid: str,
        revision: str,
        pages: List[int],
        style: QRCodeStyleEnum = QRCodeStyleEnum.BLACK,
        dpi: int = 300,
        size_mm: int = 35,
        user: Optional[User] = None
    ) -> Dict[str, Any]:
        """
        Generate QR codes for multiple pages with caching
        
        Args:
            doc_uid: Document UID
            revision: Document revision
            pages: List of page numbers
            style: QR code style
            dpi: DPI for generation
            size_mm: Size in millimeters
            user: User generating the codes
            
        Returns:
            QR code generation results
        """
        try:
            # Check cache for existing QR codes
            cached_results = await self._get_cached_qr_codes(doc_uid, revision, pages, style, dpi, size_mm)
            if cached_results:
                logger.info("QR codes retrieved from cache", doc_uid=doc_uid, revision=revision, pages=pages)
                return cached_results
            
            # Generate new QR codes
            qr_results = self.generator.generate_qr_codes(
                doc_uid=doc_uid,
                revision=revision,
                pages=pages,
                style=style,
                dpi=dpi,
                size_mm=size_mm
            )
            
            # Build response
            response = {
                "doc_uid": doc_uid,
                "revision": revision,
                "items": []
            }
            
            for qr_result in qr_results:
                # Create QR code item
                item = {
                    "page": qr_result["page"],
                    "format": QRCodeFormatEnum.PNG.value,
                    "data_base64": qr_result["data"]["png"],
                    "url": qr_result["url"]
                }
                response["items"].append(item)
                
                # Log QR code generation
                await self._log_qr_generation(
                    doc_uid=doc_uid,
                    revision=revision,
                    page=qr_result["page"],
                    user=user
                )
            
            # Cache the results
            await self._cache_qr_codes(doc_uid, revision, pages, style, dpi, size_mm, response)
            
            logger.info(
                "QR codes generated successfully",
                doc_uid=doc_uid,
                revision=revision,
                pages=pages,
                count=len(pages)
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "Failed to generate QR codes",
                doc_uid=doc_uid,
                revision=revision,
                pages=pages,
                error=str(e),
                exc_info=True
            )
            raise
    
    async def generate_single_qr_code(
        self,
        doc_uid: str,
        revision: str,
        page: int,
        style: QRCodeStyleEnum = QRCodeStyleEnum.BLACK,
        dpi: int = 300,
        size_mm: int = 35,
        user: Optional[User] = None
    ) -> Dict[str, Any]:
        """
        Generate a single QR code
        
        Args:
            doc_uid: Document UID
            revision: Document revision
            page: Page number
            style: QR code style
            dpi: DPI for generation
            size_mm: Size in millimeters
            user: User generating the code
            
        Returns:
            Single QR code result
        """
        result = await self.generate_qr_codes(
            doc_uid=doc_uid,
            revision=revision,
            pages=[page],
            style=style,
            dpi=dpi,
            size_mm=size_mm,
            user=user
        )
        
        return result["items"][0] if result["items"] else None
    
    async def verify_qr_signature(
        self,
        doc_uid: str,
        revision: str,
        page: int,
        timestamp: int,
        signature: str
    ) -> bool:
        """
        Verify QR code signature
        
        Args:
            doc_uid: Document UID
            revision: Document revision
            page: Page number
            timestamp: Timestamp from QR code
            signature: HMAC signature
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            is_valid = self.hmac_signer.verify_signature(
                doc_uid=doc_uid,
                revision=revision,
                page=page,
                timestamp=timestamp,
                signature=signature
            )
            
            logger.info(
                "QR signature verification",
                doc_uid=doc_uid,
                revision=revision,
                page=page,
                is_valid=is_valid
            )
            
            return is_valid
            
        except Exception as e:
            logger.error(
                "QR signature verification failed",
                doc_uid=doc_uid,
                revision=revision,
                page=page,
                error=str(e),
                exc_info=True
            )
            return False
    
    async def get_qr_url(
        self,
        doc_uid: str,
        revision: str,
        page: int
    ) -> str:
        """
        Generate QR code URL with signature
        
        Args:
            doc_uid: Document UID
            revision: Document revision
            page: Page number
            
        Returns:
            Signed QR code URL
        """
        return self.hmac_signer.generate_qr_url(doc_uid, revision, page)
    
    async def _get_cached_qr_codes(
        self,
        doc_uid: str,
        revision: str,
        pages: List[int],
        style: QRCodeStyleEnum,
        dpi: int,
        size_mm: int
    ) -> Optional[Dict[str, Any]]:
        """Get QR codes from cache"""
        cache_key = f"qr_codes:{doc_uid}:{revision}:{style.value}:{dpi}:{size_mm}:{','.join(map(str, pages))}"
        return await cache_manager.get(cache_key)
    
    async def _cache_qr_codes(
        self,
        doc_uid: str,
        revision: str,
        pages: List[int],
        style: QRCodeStyleEnum,
        dpi: int,
        size_mm: int,
        data: Dict[str, Any]
    ):
        """Cache QR codes"""
        cache_key = f"qr_codes:{doc_uid}:{revision}:{style.value}:{dpi}:{size_mm}:{','.join(map(str, pages))}"
        await cache_manager.set(cache_key, data, ttl=self.cache_ttl)
    
    async def _log_qr_generation(
        self,
        doc_uid: str,
        revision: str,
        page: int,
        user: Optional[User] = None
    ):
        """Log QR code generation to database"""
        try:
            db = next(get_db())
            
            qr_log = QRCodeModel(
                doc_uid=doc_uid,
                revision=revision,
                page=page,
                generated_at=datetime.utcnow(),
                generated_by=user.id if user else None
            )
            
            db.add(qr_log)
            db.commit()
            
        except Exception as e:
            logger.error(
                "Failed to log QR code generation",
                doc_uid=doc_uid,
                revision=revision,
                page=page,
                error=str(e)
            )
    
    async def get_qr_generation_history(
        self,
        doc_uid: Optional[str] = None,
        user_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get QR code generation history
        
        Args:
            doc_uid: Filter by document UID
            user_id: Filter by user ID
            limit: Maximum number of records
            
        Returns:
            List of QR code generation records
        """
        try:
            db = next(get_db())
            
            query = db.query(QRCodeModel)
            
            if doc_uid:
                query = query.filter(QRCodeModel.doc_uid == doc_uid)
            
            if user_id:
                query = query.filter(QRCodeModel.generated_by == user_id)
            
            records = query.order_by(QRCodeModel.generated_at.desc()).limit(limit).all()
            
            return [
                {
                    "id": record.id,
                    "doc_uid": record.doc_uid,
                    "revision": record.revision,
                    "page": record.page,
                    "generated_at": record.generated_at,
                    "generated_by": record.generated_by
                }
                for record in records
            ]
            
        except Exception as e:
            logger.error(
                "Failed to get QR generation history",
                doc_uid=doc_uid,
                user_id=user_id,
                error=str(e),
                exc_info=True
            )
            return []
    
    async def invalidate_qr_cache(self, doc_uid: str, revision: Optional[str] = None):
        """
        Invalidate QR code cache
        
        Args:
            doc_uid: Document UID
            revision: Optional revision to invalidate
        """
        try:
            if revision:
                pattern = f"qr_codes:{doc_uid}:{revision}:*"
            else:
                pattern = f"qr_codes:{doc_uid}:*"
            
            deleted_count = await cache_manager.delete_pattern(pattern)
            
            logger.info(
                "QR cache invalidated",
                doc_uid=doc_uid,
                revision=revision,
                deleted_keys=deleted_count
            )
            
        except Exception as e:
            logger.error(
                "Failed to invalidate QR cache",
                doc_uid=doc_uid,
                revision=revision,
                error=str(e)
            )


# Global service instance
qr_service = QRCodeService()
