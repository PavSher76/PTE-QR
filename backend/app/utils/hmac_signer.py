"""
HMAC signature utilities for QR code URL validation
"""

import hmac
import hashlib
import time
from typing import Optional
from app.core.config import settings


class HMACSigner:
    """HMAC signature generator and validator for QR URLs"""

    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or settings.QR_HMAC_SECRET.encode("utf-8")

    def generate_signature(
        self, doc_uid: str, revision: str, page: int, timestamp: Optional[int] = None
    ) -> str:
        """
        Generate HMAC signature for QR URL parameters

        Args:
            doc_uid: Document UID
            revision: Document revision
            page: Page number
            timestamp: Unix timestamp (defaults to current time)

        Returns:
            HMAC signature as hex string
        """
        if timestamp is None:
            timestamp = int(time.time())

        # Create message string: {docUid}|{rev}|{page}|{ts}
        message = f"{doc_uid}|{revision}|{page}|{timestamp}"

        # Generate HMAC-SHA256 signature
        signature = hmac.new(
            self.secret_key, message.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        return signature

    def verify_signature(
        self, doc_uid: str, revision: str, page: int, timestamp: int, signature: str
    ) -> bool:
        """
        Verify HMAC signature for QR URL parameters

        Args:
            doc_uid: Document UID
            revision: Document revision
            page: Page number
            timestamp: Unix timestamp
            signature: Signature to verify

        Returns:
            True if signature is valid, False otherwise
        """
        expected_signature = self.generate_signature(doc_uid, revision, page, timestamp)

        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(expected_signature, signature)

    def generate_qr_url(
        self,
        doc_uid: str,
        revision: str,
        page: int,
        base_url: str = "https://qr.pti.ru",
    ) -> str:
        """
        Generate complete QR URL with signature

        Args:
            doc_uid: Document UID
            revision: Document revision
            page: Page number
            base_url: Base URL for QR resolution

        Returns:
            Complete QR URL with signature
        """
        timestamp = int(time.time())
        signature = self.generate_signature(doc_uid, revision, page, timestamp)

        return f"{base_url}/r/{doc_uid}/{revision}/{page}?ts={timestamp}&t={signature}"

    def parse_qr_url(self, url: str) -> Optional[dict]:
        """
        Parse QR URL and extract parameters

        Args:
            url: QR URL to parse

        Returns:
            Dictionary with parsed parameters or None if invalid
        """
        try:
            # Extract path parameters: /r/{docUid}/{rev}/{page}
            parts = url.split("/r/")
            if len(parts) != 2:
                return None

            path_part = parts[1].split("?")[0]
            path_params = path_part.split("/")
            if len(path_params) != 3:
                return None

            doc_uid, revision, page_str = path_params

            # Extract query parameters
            query_part = url.split("?")[1] if "?" in url else ""
            query_params = {}
            for param in query_part.split("&"):
                if "=" in param:
                    key, value = param.split("=", 1)
                    query_params[key] = value

            timestamp = int(query_params.get("ts", 0))
            signature = query_params.get("t", "")

            return {
                "doc_uid": doc_uid,
                "revision": revision,
                "page": int(page_str),
                "timestamp": timestamp,
                "signature": signature,
            }
        except (ValueError, IndexError):
            return None
