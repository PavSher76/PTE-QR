"""
Service for QR code generation
"""

import qrcode
import hmac
import hashlib
import json
from typing import Dict, Any
from io import BytesIO
from PIL import Image
import structlog

from app.core.config import settings
from app.core.logging import DebugLogger, log_function_call, log_function_result

logger = structlog.get_logger()
debug_logger = DebugLogger(__name__)

class QRService:
    """Service for QR code generation and validation"""

    def __init__(self):
        log_function_call("QRService.__init__")
        self.hmac_secret = settings.QR_HMAC_SECRET
        self.qr_size = settings.QR_CODE_SIZE
        self.qr_border = settings.QR_CODE_BORDER
        self.error_correction = settings.QR_CODE_ERROR_CORRECTION
        
        debug_logger.info(
            "QRService initialized",
            qr_size=self.qr_size,
            qr_border=self.qr_border,
            error_correction=self.error_correction
        )
        log_function_result("QRService.__init__", qr_size=self.qr_size)

    def generate_qr_data(
        self, 
        enovia_id: str, 
        revision: str, 
        page_number: int,
        url_prefix: str = None
    ) -> str:
        """
        Generate QR code data with HMAC signature
        """
        log_function_call(
            "QRService.generate_qr_data",
            enovia_id=enovia_id,
            revision=revision,
            page_number=page_number,
            url_prefix=url_prefix
        )
        
        try:
            debug_logger.debug(
                "Generating QR code data",
                enovia_id=enovia_id,
                revision=revision,
                page_number=page_number
            )
            
            # Get URL prefix from settings or use default
            if not url_prefix:
                url_prefix = "https://pte-qr.example.com"
            
            # Create the base URL
            base_url = f"{url_prefix}/r/{enovia_id}/{revision}/{page_number}"
            
            debug_logger.debug("Created base URL", base_url=base_url)
            
            # Create data payload
            payload = {
                "enovia_id": enovia_id,
                "revision": revision,
                "page_number": page_number,
                "url": base_url
            }
            
            # Create HMAC signature
            payload_json = json.dumps(payload, sort_keys=True)
            signature = hmac.new(
                self.hmac_secret.encode('utf-8'),
                payload_json.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Add signature to payload
            payload["signature"] = signature
            
            # Return the complete URL with signature
            return f"{base_url}?sig={signature}"
            
        except Exception as e:
            logger.error(f"Error generating QR data", error=str(e))
            raise

    def generate_qr_code_image(self, qr_data: str) -> BytesIO:
        """
        Generate QR code image from data
        """
        logger.debug("Generating QR code image", qr_data=qr_data)
        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=getattr(qrcode.constants, f'ERROR_CORRECT_{self.error_correction}'),
                box_size=10,
                border=self.qr_border,
            )
            
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to BytesIO
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            return img_buffer
            
        except Exception as e:
            logger.error(f"Error generating QR code image", error=str(e))
            raise

    def verify_qr_signature(self, qr_data: str) -> bool:
        """
        Verify HMAC signature of QR code data
        """
        try:
            logger.debug("Verifying QR signature", qr_data=qr_data)
            # Parse URL and extract signature
            if '?sig=' not in qr_data:
                return False
                
            base_url, signature = qr_data.split('?sig=')
            
            # Extract components from URL
            # Expected format: /r/{enovia_id}/{revision}/{page_number}
            parts = base_url.split('/')
            if len(parts) < 5 or parts[-4] != 'r':
                return False
                
            enovia_id = parts[-3]
            revision = parts[-2]
            page_number = int(parts[-1])
            
            # Recreate payload
            payload = {
                "enovia_id": enovia_id,
                "revision": revision,
                "page_number": page_number,
                "url": base_url
            }
            
            # Generate expected signature
            payload_json = json.dumps(payload, sort_keys=True)
            expected_signature = hmac.new(
                self.hmac_secret.encode('utf-8'),
                payload_json.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Error verifying QR signature", error=str(e))
            return False

    def parse_qr_data(self, qr_data: str) -> Dict[str, Any]:
        """
        Parse QR code data and extract components
        """
        try:
            logger.debug("Parsing QR data", qr_data=qr_data)
            if '?sig=' not in qr_data:
                raise ValueError("Invalid QR code format")
                
            base_url, signature = qr_data.split('?sig=')
            
            # Extract components from URL
            parts = base_url.split('/')
            if len(parts) < 5 or parts[-4] != 'r':
                raise ValueError("Invalid QR code URL format")
                
            return {
                "enovia_id": parts[-3],
                "revision": parts[-2],
                "page_number": int(parts[-1]),
                "url": base_url,
                "signature": signature
            }
            
        except Exception as e:
            logger.error(f"Error parsing QR data", error=str(e))
            raise

    def generate_qr_data_with_hmac(
        self, payload: dict, base_url_prefix: str, expires_in_minutes: int = 1440
    ) -> tuple[str, str]:
        """
        Generates QR data with an HMAC signature and embeds it into a URL.

        Args:
            payload: The data to be embedded in the QR code (e.g., document ID, revision, page).
            base_url_prefix: The base URL prefix for the QR code (e.g., "http://localhost:3000/r").
            expires_in_minutes: The expiration time for the QR code in minutes.

        Returns:
            A tuple containing:
            - The full URL with encoded QR data and signature.
            - The raw HMAC signature.
        """
        try:
            logger.debug("Generating QR data with HMAC", payload=payload, base_url_prefix=base_url_prefix, expires_in_minutes=expires_in_minutes)
            # Add expiration to payload
            from datetime import datetime, timedelta
            expiration_time = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
            payload["exp"] = int(expiration_time.timestamp())

            json_payload = json.dumps(payload, sort_keys=True, separators=(",", ":"))
            signature = hmac.new(
                self.hmac_secret.encode("utf-8"),
                json_payload.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()

            # Construct URL like: {base_url_prefix}/{enovia_id}/{revision}/{page_number}/{signature}
            qr_data_url = (
                f"{base_url_prefix}/"
                f"{payload['enovia_id']}/"
                f"{payload['revision']}/"
                f"{payload['page']}/"
                f"{signature}"
            )

            logger.debug("Generated QR data URL", qr_data_url=qr_data_url)
            return qr_data_url, signature
        except Exception as e:
            logger.error(f"Error generating QR data with HMAC", error=str(e))
            raise

    def generate_qr_code_image(
        self,
        data: str,
        size: int = None,
        border: int = None,
        error_correction: str = None,
    ) -> bytes:
        """
        Generates a QR code image for the given data.

        Args:
            data: The data to encode in the QR code.
            size: The size of the QR code in pixels.
            border: The border size around the QR code.
            error_correction: Error correction level (L, M, Q, H).

        Returns:
            The QR code image as bytes.
        """
        try:
            logger.debug("Generating QR code image", data=data, size=size, border=border, error_correction=error_correction)
            # Use defaults if not provided
            if size is None:
                size = self.qr_size
            if border is None:
                border = self.qr_border
            if error_correction is None:
                error_correction = self.error_correction

            if error_correction == "L":
                error_correction_level = qrcode.constants.ERROR_CORRECT_L
            elif error_correction == "M":
                error_correction_level = qrcode.constants.ERROR_CORRECT_M
            elif error_correction == "Q":
                error_correction_level = qrcode.constants.ERROR_CORRECT_Q
            elif error_correction == "H":
                error_correction_level = qrcode.constants.ERROR_CORRECT_H
            else:
                error_correction_level = qrcode.constants.ERROR_CORRECT_M

            qr = qrcode.QRCode(
                version=None,
                error_correction=error_correction_level,
                box_size=size // 29,  # Adjust box_size based on desired total size
                border=border,
            )
            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            img_buffer = BytesIO()
            img.save(img_buffer, format="PNG")
            img_buffer.seek(0)
            return img_buffer.getvalue()
        except Exception as e:
            logger.error(f"Error generating QR code image", error=str(e))
            raise


# Global QR service instance - will be created lazily
_qr_service_instance = None


def get_qr_service() -> QRService:
    """Get QR service instance (lazy initialization)"""
    global _qr_service_instance
    if _qr_service_instance is None:
        _qr_service_instance = QRService()
    return _qr_service_instance


# For backward compatibility
qr_service = get_qr_service()