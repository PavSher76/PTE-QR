"""
Test database configuration and session management
"""

import os
import tempfile
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.test_config import test_settings

# Create a temporary SQLite database for tests
test_db_path = tempfile.mktemp(suffix=".db")
test_database_url = f"sqlite:///{test_db_path}"

# SQLite database engine for tests
test_engine = create_engine(
    test_database_url,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,  # Set to True for SQL debugging
)

# Test session factory
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Test base class
TestBase = declarative_base()


def get_test_db():
    """Get test database session"""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_test_tables():
    """Create test tables"""
    from app.models.user import Base as UserBase
    from app.models.document import Base as DocumentBase
    from app.models.qr_code import Base as QRCodeBase
    from app.models.audit import Base as AuditBase
    
    # Create all tables in correct order (users first, then documents)
    UserBase.metadata.create_all(bind=test_engine)
    DocumentBase.metadata.create_all(bind=test_engine)
    QRCodeBase.metadata.create_all(bind=test_engine)
    AuditBase.metadata.create_all(bind=test_engine)


def drop_test_tables():
    """Drop test tables"""
    from app.models.user import Base as UserBase
    from app.models.document import Base as DocumentBase
    from app.models.qr_code import Base as QRCodeBase
    from app.models.audit import Base as AuditBase
    
    # Drop all tables in reverse order
    AuditBase.metadata.drop_all(bind=test_engine)
    QRCodeBase.metadata.drop_all(bind=test_engine)
    DocumentBase.metadata.drop_all(bind=test_engine)
    UserBase.metadata.drop_all(bind=test_engine)


def cleanup_test_db():
    """Clean up test database file"""
    if os.path.exists(test_db_path):
        os.unlink(test_db_path)
