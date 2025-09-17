"""
Unit tests for HMAC signer utility
"""

import time

import pytest

from app.utils.hmac_signer import HMACSigner


class TestHMACSigner:
    """Test HMAC signer functionality"""

    def setup_method(self):
        """Set up test fixtures."""
        self.signer = HMACSigner()
        self.doc_uid = "TEST-DOC-001"
        self.revision = "A"
        self.page = 1

    def test_generate_signature(self):
        """Test signature generation."""
        timestamp = int(time.time())
        signature = self.signer.generate_signature(
            self.doc_uid, self.revision, self.page, timestamp
        )

        assert signature is not None
        assert isinstance(signature, str)
        assert len(signature) > 0

    def test_verify_signature_valid(self):
        """Test signature verification with valid signature."""
        timestamp = int(time.time())
        signature = self.signer.generate_signature(
            self.doc_uid, self.revision, self.page, timestamp
        )

        is_valid = self.signer.verify_signature(
            self.doc_uid, self.revision, self.page, timestamp, signature
        )

        assert is_valid is True

    def test_verify_signature_invalid(self):
        """Test signature verification with invalid signature."""
        timestamp = int(time.time())
        invalid_signature = "invalid_signature"

        is_valid = self.signer.verify_signature(
            self.doc_uid, self.revision, self.page, timestamp, invalid_signature
        )

        assert is_valid is False

    def test_verify_signature_wrong_timestamp(self):
        """Test signature verification with wrong timestamp."""
        timestamp = int(time.time())
        signature = self.signer.generate_signature(
            self.doc_uid, self.revision, self.page, timestamp
        )

        wrong_timestamp = timestamp + 1
        is_valid = self.signer.verify_signature(
            self.doc_uid, self.revision, self.page, wrong_timestamp, signature
        )

        assert is_valid is False

    def test_generate_qr_url(self):
        """Test QR URL generation."""
        url = self.signer.generate_qr_url(self.doc_uid, self.revision, self.page)

        assert url is not None
        assert isinstance(url, str)
        assert self.doc_uid in url
        assert self.revision in url
        assert str(self.page) in url
        assert "t=" in url  # signature parameter
        assert "ts=" in url  # timestamp parameter

    def test_signature_consistency(self):
        """Test that same inputs produce same signature."""
        timestamp = int(time.time())

        signature1 = self.signer.generate_signature(
            self.doc_uid, self.revision, self.page, timestamp
        )
        signature2 = self.signer.generate_signature(
            self.doc_uid, self.revision, self.page, timestamp
        )

        assert signature1 == signature2

    def test_different_inputs_different_signatures(self):
        """Test that different inputs produce different signatures."""
        timestamp = int(time.time())

        signature1 = self.signer.generate_signature(
            self.doc_uid, self.revision, self.page, timestamp
        )
        signature2 = self.signer.generate_signature(
            self.doc_uid, self.revision, self.page + 1, timestamp
        )

        assert signature1 != signature2

    def test_signature_with_special_characters(self):
        """Test signature generation with special characters in input."""
        doc_uid_with_special = "TEST-DOC-001@#$%"
        revision_with_special = "A-1.0"
        timestamp = int(time.time())

        signature = self.signer.generate_signature(
            doc_uid_with_special, revision_with_special, self.page, timestamp
        )

        assert signature is not None
        assert isinstance(signature, str)

        # Verify the signature
        is_valid = self.signer.verify_signature(
            doc_uid_with_special, revision_with_special, self.page, timestamp, signature
        )

        assert is_valid is True
