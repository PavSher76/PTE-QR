"""
ENOVIA PLM integration service
"""

from datetime import datetime
from typing import Any, Dict, Optional

import httpx
import structlog
from app.core.config import settings
from app.models.document import DocumentStatusEnum

logger = structlog.get_logger()


class ENOVIAClient:
    """ENOVIA PLM client"""

    def __init__(self):
        self.base_url = settings.ENOVIA_BASE_URL
        self.client_id = settings.ENOVIA_CLIENT_ID
        self.client_secret = settings.ENOVIA_CLIENT_SECRET
        self.access_token = None
        self.token_expires_at = None

    async def _get_access_token(self) -> str:
        """Get OAuth2 access token"""
        if (
            self.access_token
            and self.token_expires_at
            and datetime.now() < self.token_expires_at
        ):
            return self.access_token

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/oauth2/token",
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "scope": "read",
                    },
                    timeout=30.0,
                )
                response.raise_for_status()

                token_data = response.json()
                self.access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires_at = (
                    datetime.now().timestamp() + expires_in - 60
                )  # 1 minute buffer

                logger.info("ENOVIA access token obtained")
                return self.access_token

        except Exception as e:
            logger.error("Failed to get ENOVIA access token", error=str(e))
            raise

    async def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> Dict[str, Any]:
        """Make authenticated request to ENOVIA"""
        try:
            token = await self._get_access_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                **kwargs.get("headers", {}),
            }
            kwargs["headers"] = headers

            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method, f"{self.base_url}{endpoint}", timeout=30.0, **kwargs
                )
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(
                "ENOVIA API error",
                method=method,
                endpoint=endpoint,
                status_code=e.response.status_code,
                response=e.response.text,
            )
            raise
        except Exception as e:
            logger.error(
                "ENOVIA request failed", method=method, endpoint=endpoint, error=str(e)
            )
            raise

    async def get_document_meta(self, doc_uid: str) -> Optional[Dict[str, Any]]:
        """Get document metadata from ENOVIA"""
        try:
            data = await self._make_request("GET", f"/api/v1/documents/{doc_uid}")

            return {
                "id": data.get("id"),
                "title": data.get("title"),
                "number": data.get("number"),
                "type": data.get("type"),
                "created_at": data.get("createdAt"),
                "updated_at": data.get("updatedAt"),
            }

        except Exception as e:
            logger.error(
                "Failed to get document metadata", doc_uid=doc_uid, error=str(e)
            )
            return None

    async def get_revision_meta(
        self, doc_uid: str, revision: str
    ) -> Optional[Dict[str, Any]]:
        """Get revision metadata from ENOVIA"""
        try:
            data = await self._make_request(
                "GET", f"/api/v1/documents/{doc_uid}/revisions/{revision}"
            )

            return {
                "id": data.get("id"),
                "revision": data.get("revision"),
                "maturityState": data.get("maturityState"),
                "releasedDate": data.get("releasedDate"),
                "supersededBy": data.get("supersededBy"),
                "lastModified": data.get("lastModified"),
                "pages": data.get("pages", 1),
            }

        except Exception as e:
            logger.error(
                "Failed to get revision metadata",
                doc_uid=doc_uid,
                revision=revision,
                error=str(e),
            )
            return None

    async def get_latest_released(self, doc_uid: str) -> Optional[Dict[str, Any]]:
        """Get latest released revision from ENOVIA"""
        try:
            data = await self._make_request(
                "GET", f"/api/v1/documents/{doc_uid}/revisions/latest"
            )

            return {
                "id": data.get("id"),
                "revision": data.get("revision"),
                "maturityState": data.get("maturityState"),
                "releasedDate": data.get("releasedDate"),
                "lastModified": data.get("lastModified"),
            }

        except Exception as e:
            logger.error(
                "Failed to get latest released revision", doc_uid=doc_uid, error=str(e)
            )
            return None

    def map_enovia_state_to_business_status(
        self, enovia_state: str
    ) -> DocumentStatusEnum:
        """Map ENOVIA state to business status"""
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

    def is_revision_actual(self, revision_data: Dict[str, Any]) -> bool:
        """Check if revision is actual (not superseded)"""
        maturity_state = revision_data.get("maturityState", "")
        superseded_by = revision_data.get("supersededBy")

        # Revision is actual if it's released and not superseded
        return (
            maturity_state in ["Released", "AFC", "Accepted", "Approved"]
            and not superseded_by
        )

    async def health_check(self) -> Dict[str, Any]:
        """Check ENOVIA service health"""
        try:
            await self._make_request("GET", "/api/v1/health")
            return {"enovia": "healthy", "last_check": datetime.now().isoformat()}
        except Exception as e:
            logger.error("ENOVIA health check failed", error=str(e))
            return {
                "enovia": "unhealthy",
                "error": str(e),
                "last_check": datetime.now().isoformat(),
            }


# Global ENOVIA service instance
enovia_service = ENOVIAClient()
