"""
Pytest configuration and fixtures
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings
from app.models.user import User
from app.models.document import Document, DocumentRevision
from app.core.cache import cache_manager

# Test database URL - use PostgreSQL for tests
SQLALCHEMY_DATABASE_URL = "postgresql://pte_qr:pte_qr_dev@postgres:5432/pte_qr_test"

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
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def db_session() -> Generator:
    """Create a test database session."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


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
async def test_user(db_session) -> User:
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
        role="user"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
async def test_admin_user(db_session) -> User:
    """Create a test admin user."""
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
        role="admin"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
async def test_document(db_session) -> Document:
    """Create a test document."""
    document = Document(
        doc_uid="TEST-DOC-001",
        title="Test Document",
        number="TD-001",
        enovia_id="12345"
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)
    return document


@pytest.fixture
async def test_document_revision(db_session, test_document) -> DocumentRevision:
    """Create a test document revision."""
    revision = DocumentRevision(
        document_id=test_document.id,
        revision="A",
        enovia_state="Released",
        business_status="APPROVED_FOR_CONSTRUCTION",
        released_at="2024-01-01T00:00:00Z",
        superseded_by=None,
        last_modified="2024-01-01T00:00:00Z",
        enovia_revision_id="12345-A",
        maturity_state="Released"
    )
    db_session.add(revision)
    db_session.commit()
    db_session.refresh(revision)
    return revision


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
        "url": "https://qr.pti.ru/r/TEST-DOC-001/A/1?t=signature&ts=1234567890"
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
            "openLatest": None
        }
    }
