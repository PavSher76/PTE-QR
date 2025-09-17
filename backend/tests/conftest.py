"""
Pytest configuration and fixtures
"""

from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.core.test_cache import test_cache_service
from app.core.test_database import (
    TestSessionLocal,
    cleanup_test_db,
    create_test_tables,
    drop_test_tables,
)
from app.main import app as fastapi_app
from app.models.document import Document
from app.models.user import User
from app.services.auth_service import AuthService
from app.api.dependencies import get_current_user, get_current_user_optional
import app.services.auth_service

# Create test auth service with test settings
test_auth_service = AuthService()

# Override auth service in dependencies


# Mock the auth service
def mock_get_auth_service():
    return test_auth_service


# Override the auth service function

app.services.auth_service.get_auth_service = mock_get_auth_service

# Also override the global auth_service instance
app.services.auth_service._auth_service_instance = test_auth_service


# Mock the get_user_by_username method to return test user
async def mock_get_user_by_username(username: str, db):
    """Mock get_user_by_username to return test user"""
    if username == "testuser":
        return db.query(User).filter(User.username == "testuser").first()
    return None


# Override the method
test_auth_service.get_user_by_username = mock_get_user_by_username

# Override app settings for tests will be done in fixtures


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def setup_test_db():
    """Set up test database tables."""
    create_test_tables()
    yield
    drop_test_tables()
    cleanup_test_db()


@pytest.fixture
def db_session(setup_test_db) -> Generator:
    """Create a test database session."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session) -> Generator:
    """Create a test client with database session override."""
    # Override database dependency
    fastapi_app.dependency_overrides[get_db] = lambda: TestSessionLocal()

    with TestClient(fastapi_app) as test_client:
        yield test_client

    # Clean up only database dependency
    fastapi_app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def authenticated_client(db_session, test_user) -> Generator:
    """Create an authenticated test client."""

    def mock_get_current_user():
        return test_user

    def mock_get_current_user_optional():
        return test_user

    # Store original overrides
    original_overrides = fastapi_app.dependency_overrides.copy()

    # Override all dependencies
    fastapi_app.dependency_overrides[get_db] = lambda: TestSessionLocal()
    fastapi_app.dependency_overrides[get_current_user] = mock_get_current_user
    fastapi_app.dependency_overrides[get_current_user_optional] = (
        mock_get_current_user_optional
    )

    with TestClient(fastapi_app) as test_client:
        yield test_client

    # Restore original overrides
    fastapi_app.dependency_overrides.clear()
    fastapi_app.dependency_overrides.update(original_overrides)


@pytest.fixture
def unauthenticated_client(db_session) -> Generator:
    """Create an unauthenticated test client that will return 401/403 for protected endpoints."""
    from fastapi import HTTPException

    def mock_get_current_user():
        raise HTTPException(status_code=401, detail="Not authenticated")

    def mock_get_current_user_optional():
        print(
            "🔍 unauthenticated_client: mock_get_current_user_optional called - "
            "returning None"
        )
        return None

    # Store original overrides
    original_overrides = fastapi_app.dependency_overrides.copy()

    # Override all dependencies
    fastapi_app.dependency_overrides[get_db] = lambda: TestSessionLocal()
    fastapi_app.dependency_overrides[get_current_user] = mock_get_current_user
    fastapi_app.dependency_overrides[get_current_user_optional] = (
        mock_get_current_user_optional
    )

    with TestClient(fastapi_app) as test_client:
        yield test_client

    # Restore original overrides
    fastapi_app.dependency_overrides.clear()
    fastapi_app.dependency_overrides.update(original_overrides)


@pytest.fixture(autouse=True)
def setup_test_data(db_session):
    """Set up test data for all tests"""
    # Create test user
    from app.models.user import User

    test_user = db_session.query(User).filter(User.username == "testuser").first()
    if not test_user:
        test_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
            is_active=True,
            is_superuser=False,
        )
        db_session.add(test_user)
        db_session.commit()
        db_session.refresh(test_user)

    # Create test document
    from datetime import datetime

    from app.models.document import Document

    test_document = (
        db_session.query(Document).filter(Document.doc_uid == "TEST-DOC-001").first()
    )
    if not test_document:
        test_document = Document(
            doc_uid="TEST-DOC-001",
            title="Test Document",
            description="Test document description",
            document_type="Drawing",
            current_revision="A",
            current_page=1,
            business_status="APPROVED_FOR_CONSTRUCTION",
            enovia_state="Released",
            is_actual=True,
            released_at=datetime(2024, 1, 1, 0, 0, 0),
            superseded_by=None,
        )
        db_session.add(test_document)
        db_session.commit()
        db_session.refresh(test_document)

    yield

    # Clean up after test
    db_session.rollback()


@pytest.fixture
def mock_cache():
    """Mock cache service for testing."""
    return test_cache_service


@pytest.fixture
def test_user(db_session) -> User:
    """Get or create a test user."""
    return db_session.query(User).filter(User.username == "testuser").first()


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
    return db_session.query(Document).filter(Document.doc_uid == "TEST-DOC-001").first()


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
