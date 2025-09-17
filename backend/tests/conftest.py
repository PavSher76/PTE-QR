"""
Pytest configuration and fixtures
"""

# Test database URL - use environment variable or default
import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import get_db
from app.main import app
from app.models.document import Document
from app.models.user import User

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/pte_qr_test"
)

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def db_session() -> Generator:
    """Create a test database session."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session) -> Generator:
    """Create a test client with database session override."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session) -> User:
    """Get or create a test user."""
    # Try to get existing user first
    user = db_session.query(User).filter(User.username == "testuser").first()
    if not user:
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=(
                "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
            ),  # secret
            is_active=True,
            is_superuser=False,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


@pytest.fixture
def test_admin_user(db_session) -> User:
    """Get or create a test admin user."""
    # Try to get existing admin user first
    user = db_session.query(User).filter(User.username == "admin").first()
    if not user:
        user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=(
                "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
            ),  # secret
            is_active=True,
            is_superuser=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


@pytest.fixture
def test_document(db_session) -> Document:
    """Get or create a test document."""
    # Try to get existing document first
    document = (
        db_session.query(Document).filter(Document.doc_uid == "TEST-DOC-001").first()
    )
    if not document:
        document = Document(
            doc_uid="TEST-DOC-001",
            title="Test Document",
            description="Test document description",
            document_type="Drawing",
            current_revision="A",
            current_page=1,
            business_status="APPROVED_FOR_CONSTRUCTION",
            enovia_state="Released",
            is_actual=True,
            released_at="2024-01-01T00:00:00Z",
            superseded_by=None,
        )
        db_session.add(document)
        db_session.commit()
        db_session.refresh(document)
    return document


@pytest.fixture
async def mock_cache():
    """Mock cache for testing."""
    # This would be implemented with a mock Redis or in-memory cache
    pass


@pytest.fixture
def sample_qr_data():
    """Sample QR code data for testing."""
    return {
        "doc_uid": "TEST-DOC-001",
        "revision": "A",
        "page": 1,
        "url": "https://qr.pti.ru/r/TEST-DOC-001/A/1?t=signature&ts=1234567890",
    }


@pytest.fixture
def sample_document_status():
    """Sample document status data for testing."""
    return {
        "doc_uid": "TEST-DOC-001",
        "revision": "A",
        "page": 1,
        "business_status": "APPROVED_FOR_CONSTRUCTION",
        "enovia_state": "Released",
        "is_actual": True,
        "released_at": "2024-01-01T00:00:00Z",
        "superseded_by": None,
        "links": {
            "openDocument": "https://enovia.pti.ru/3dspace/document/TEST-DOC-001?rev=A",
            "openLatest": None,
        },
    }
