"""
ENOVIA PLM integration client
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
import structlog

from app.core.config import settings
from app.models.document import DocumentStatusEnum, EnoviaStateEnum

logger = structlog.get_logger()


class ENOVIAClient:
    """ENOVIA PLM integration client"""

    def __init__(self):
        self.base_url = settings.ENOVIA_BASE_URL
        self.client_id = settings.ENOVIA_CLIENT_ID
        self.client_secret = settings.ENOVIA_CLIENT_SECRET
        self.scope = settings.ENOVIA_SCOPE
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    async def _get_access_token(self) -> str:
        """
        Get OAuth2 access token for ENOVIA API

        Returns:
            Access token string
        """
        if (
            self._access_token
            and self._token_expires_at
            and datetime.now() < self._token_expires_at
        ):
            return self._access_token

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/oauth/token",
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "scope": self.scope,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()

                token_data = response.json()
                self._access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                self._token_expires_at = datetime.now() + datetime.timedelta(
                    seconds=expires_in - 60
                )

                logger.info("ENOVIA access token obtained")
                return self._access_token

        except Exception as e:
            logger.error(
                "Failed to get ENOVIA access token", error=str(e), exc_info=True
            )
            raise

    async def get_document_meta(self, doc_uid: str) -> Optional[Dict[str, Any]]:
        """
        Get document metadata from ENOVIA

        Args:
            doc_uid: Document UID

        Returns:
            Document metadata or None if not found
        """
        try:
            access_token = await self._get_access_token()

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/documents/{doc_uid}",
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(
                "Failed to get document metadata",
                doc_uid=doc_uid,
                error=str(e),
                exc_info=True,
            )
            return None

    async def get_revision_meta(
        self, doc_uid: str, revision: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get revision metadata from ENOVIA

        Args:
            doc_uid: Document UID
            revision: Revision identifier

        Returns:
            Revision metadata or None if not found
        """
        try:
            access_token = await self._get_access_token()

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/documents/{doc_uid}/revisions/{revision}",
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(
                "Failed to get revision metadata",
                doc_uid=doc_uid,
                revision=revision,
                error=str(e),
                exc_info=True,
            )
            return None

    async def get_latest_released(self, doc_uid: str) -> Optional[Dict[str, Any]]:
        """
        Get latest released revision from ENOVIA

        Args:
            doc_uid: Document UID

        Returns:
            Latest released revision metadata or None if not found
        """
        try:
            access_token = await self._get_access_token()

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/documents/{doc_uid}/latest-released",
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                if response.status_code == 404:
                    return None

                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(
                "Failed to get latest released revision",
                doc_uid=doc_uid,
                error=str(e),
                exc_info=True,
            )
            return None

    def map_enovia_state_to_business_status(
        self, enovia_state: str
    ) -> DocumentStatusEnum:
        """
        Map ENOVIA state to business status

        Args:
            enovia_state: ENOVIA maturity state

        Returns:
            Mapped business status
        """
        # Default mapping based on requirements
        mapping = {
            "Released": DocumentStatusEnum.APPROVED_FOR_CONSTRUCTION,
            "AFC": DocumentStatusEnum.APPROVED_FOR_CONSTRUCTION,
            "Accepted": DocumentStatusEnum.ACCEPTED_BY_CUSTOMER,
            "Approved": DocumentStatusEnum.ACCEPTED_BY_CUSTOMER,
            "Obsolete": DocumentStatusEnum.CHANGES_INTRODUCED_GET_NEW,
            "Superseded": DocumentStatusEnum.CHANGES_INTRODUCED_GET_NEW,
            "In Work": DocumentStatusEnum.IN_WORK,
            "Frozen": DocumentStatusEnum.IN_WORK,
        }

        return mapping.get(enovia_state, DocumentStatusEnum.IN_WORK)

    def is_revision_actual(self, revision_meta: Dict[str, Any]) -> bool:
        """
        Check if revision is actual (not superseded)

        Args:
            revision_meta: Revision metadata from ENOVIA

        Returns:
            True if revision is actual, False otherwise
        """
        enovia_state = revision_meta.get("maturityState", "")
        superseded_by = revision_meta.get("supersededBy")

        # Revision is actual if it's not superseded and not obsolete
        return not superseded_by and enovia_state not in ["Obsolete", "Superseded"]

    async def health_check(self) -> bool:
        """
        Check ENOVIA API health

        Returns:
            True if API is healthy, False otherwise
        """
        try:
            access_token = await self._get_access_token()

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/health",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=5.0,
                )

                return response.status_code == 200

        except Exception as e:
            logger.error("ENOVIA health check failed", error=str(e))
            return False
