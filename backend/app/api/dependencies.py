"""
API dependencies for authentication and authorization
"""

from typing import Optional

import structlog
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import auth_service

logger = structlog.get_logger()


async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Get current authenticated user from JWT token
    """
    try:
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=401, detail="Missing or invalid authorization header"
            )

        token = auth_header.split(" ")[1]

        # Verify token
        payload = auth_service.verify_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Get user
        username = payload.get("sub")
        user = await auth_service.get_user_by_username(username, db)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not user.is_active:
            raise HTTPException(status_code=403, detail="User account is deactivated")

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get current user", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_current_user_optional(
    request: Request, db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current authenticated user from JWT token (optional)
    Returns None if no valid token is provided
    """
    try:
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split(" ")[1]

        # Verify token
        payload = auth_service.verify_token(token)
        if not payload:
            return None

        # Get user
        username = payload.get("sub")
        user = await auth_service.get_user_by_username(username, db)
        if not user or not user.is_active:
            return None

        return user

    except Exception as e:
        logger.error("Failed to get current user (optional)", error=str(e))
        return None


def require_auth() -> User:
    """
    Dependency that requires authentication
    """

    def _require_auth(current_user: User = Depends(get_current_user)) -> User:
        return current_user

    return _require_auth
