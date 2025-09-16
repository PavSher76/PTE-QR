"""
ENOVIA PLM service layer
"""

import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import structlog

from app.core.config import settings
from app.utils.enovia_client import ENOVIAClient
from app.models.document import DocumentStatusEnum, EnoviaStateEnum
from app.core.cache import cache_manager

logger = structlog.get_logger()


class ENOVIAService:
    """ENOVIA PLM service for document status management"""
    
    def __init__(self):
        self.client = ENOVIAClient()
        self.cache_ttl = settings.CACHE_TTL_SECONDS
    
    async def get_document_status(
        self, 
        doc_uid: str, 
        revision: str, 
        page: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get document status with caching
        
        Args:
            doc_uid: Document UID
            revision: Revision identifier
            page: Page number
            
        Returns:
            Document status information or None if not found
        """
        cache_key = f"doc_status:{doc_uid}:{revision}:{page}"
        
        # Try to get from cache first
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            logger.info("Document status retrieved from cache", doc_uid=doc_uid, revision=revision, page=page)
            return cached_result
        
        try:
            # Get revision metadata from ENOVIA
            revision_meta = await self.client.get_revision_meta(doc_uid, revision)
            if not revision_meta:
                logger.warning("Revision not found in ENOVIA", doc_uid=doc_uid, revision=revision)
                return None
            
            # Get latest released revision for comparison
            latest_released = await self.client.get_latest_released(doc_uid)
            
            # Map ENOVIA state to business status
            enovia_state = revision_meta.get("maturityState", "")
            business_status = self.client.map_enovia_state_to_business_status(enovia_state)
            
            # Check if revision is actual
            is_actual = self.client.is_revision_actual(revision_meta)
            
            # If not actual, check if there's a newer released version
            if not is_actual and latest_released:
                latest_revision = latest_released.get("revision", "")
                if latest_revision != revision:
                    is_actual = False
                    business_status = DocumentStatusEnum.CHANGES_INTRODUCED_GET_NEW
            
            # Build response
            result = {
                "doc_uid": doc_uid,
                "revision": revision,
                "page": page,
                "business_status": business_status.value,
                "enovia_state": enovia_state,
                "is_actual": is_actual,
                "released_at": revision_meta.get("releasedAt"),
                "superseded_by": revision_meta.get("supersededBy"),
                "links": self._build_links(doc_uid, revision, page, is_actual, latest_released)
            }
            
            # Cache the result
            await cache_manager.set(cache_key, result, ttl=self.cache_ttl)
            
            logger.info(
                "Document status retrieved from ENOVIA",
                doc_uid=doc_uid,
                revision=revision,
                page=page,
                business_status=business_status.value,
                is_actual=is_actual
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Failed to get document status",
                doc_uid=doc_uid,
                revision=revision,
                page=page,
                error=str(e),
                exc_info=True
            )
            return None
    
    def _build_links(
        self, 
        doc_uid: str, 
        revision: str, 
        page: int, 
        is_actual: bool,
        latest_released: Optional[Dict[str, Any]]
    ) -> Dict[str, Optional[str]]:
        """
        Build action links for document status response
        
        Args:
            doc_uid: Document UID
            revision: Revision identifier
            page: Page number
            is_actual: Whether revision is actual
            latest_released: Latest released revision metadata
            
        Returns:
            Dictionary of action links
        """
        links = {
            "openDocument": None,
            "openLatest": None
        }
        
        # Link to open current document (if user has access)
        if is_actual:
            links["openDocument"] = f"{settings.ENOVIA_BASE_URL}/documents/{doc_uid}/revisions/{revision}/pages/{page}"
        
        # Link to open latest released revision (if different from current)
        if not is_actual and latest_released:
            latest_revision = latest_released.get("revision", "")
            if latest_revision != revision:
                links["openLatest"] = f"{settings.ENOVIA_BASE_URL}/documents/{doc_uid}/revisions/{latest_revision}"
        
        return links
    
    async def get_document_metadata(self, doc_uid: str) -> Optional[Dict[str, Any]]:
        """
        Get document metadata with caching
        
        Args:
            doc_uid: Document UID
            
        Returns:
            Document metadata or None if not found
        """
        cache_key = f"doc_meta:{doc_uid}"
        
        # Try to get from cache first
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            logger.info("Document metadata retrieved from cache", doc_uid=doc_uid)
            return cached_result
        
        try:
            metadata = await self.client.get_document_meta(doc_uid)
            if metadata:
                # Cache the result
                await cache_manager.set(cache_key, metadata, ttl=self.cache_ttl)
                logger.info("Document metadata retrieved from ENOVIA", doc_uid=doc_uid)
            
            return metadata
            
        except Exception as e:
            logger.error(
                "Failed to get document metadata",
                doc_uid=doc_uid,
                error=str(e),
                exc_info=True
            )
            return None
    
    async def get_latest_released_revision(self, doc_uid: str) -> Optional[Dict[str, Any]]:
        """
        Get latest released revision with caching
        
        Args:
            doc_uid: Document UID
            
        Returns:
            Latest released revision metadata or None if not found
        """
        cache_key = f"latest_released:{doc_uid}"
        
        # Try to get from cache first
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            logger.info("Latest released revision retrieved from cache", doc_uid=doc_uid)
            return cached_result
        
        try:
            latest_released = await self.client.get_latest_released(doc_uid)
            if latest_released:
                # Cache the result
                await cache_manager.set(cache_key, latest_released, ttl=self.cache_ttl)
                logger.info("Latest released revision retrieved from ENOVIA", doc_uid=doc_uid)
            
            return latest_released
            
        except Exception as e:
            logger.error(
                "Failed to get latest released revision",
                doc_uid=doc_uid,
                error=str(e),
                exc_info=True
            )
            return None
    
    async def invalidate_document_cache(self, doc_uid: str, revision: Optional[str] = None):
        """
        Invalidate cache for document
        
        Args:
            doc_uid: Document UID
            revision: Optional revision to invalidate (if None, invalidates all revisions)
        """
        try:
            if revision:
                # Invalidate specific revision
                cache_keys = [
                    f"doc_status:{doc_uid}:{revision}:*",
                    f"doc_meta:{doc_uid}",
                    f"latest_released:{doc_uid}"
                ]
            else:
                # Invalidate all revisions for document
                cache_keys = [
                    f"doc_status:{doc_uid}:*",
                    f"doc_meta:{doc_uid}",
                    f"latest_released:{doc_uid}"
                ]
            
            for pattern in cache_keys:
                await cache_manager.delete_pattern(pattern)
            
            logger.info("Document cache invalidated", doc_uid=doc_uid, revision=revision)
            
        except Exception as e:
            logger.error(
                "Failed to invalidate document cache",
                doc_uid=doc_uid,
                revision=revision,
                error=str(e),
                exc_info=True
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on ENOVIA integration
        
        Returns:
            Health check results
        """
        try:
            is_healthy = await self.client.health_check()
            
            return {
                "enovia": "healthy" if is_healthy else "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "base_url": self.client.base_url
            }
            
        except Exception as e:
            logger.error("ENOVIA health check failed", error=str(e))
            return {
                "enovia": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }


# Global service instance
enovia_service = ENOVIAService()
