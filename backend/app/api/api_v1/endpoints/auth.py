"""
Authentication endpoints
"""

import time

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth_service import auth_service
from app.services.metrics_service import metrics_service
from app.core.logging import DebugLogger, log_api_request, log_api_response

router = APIRouter()
logger = structlog.get_logger()
debug_logger = DebugLogger(__name__)


@router.post("/login")
async def login(credentials: dict, request: Request, db: Session = Depends(get_db)):
    """
    User login endpoint
    """
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")

    log_api_request("POST", "/login", client_ip=client_ip, user_agent=user_agent)
    debug_logger.info("Login attempt started", client_ip=client_ip, user_agent=user_agent)

    try:
        username = credentials.get("username")
        password = credentials.get("password")

        debug_logger.debug(
            "Login credentials received", 
            username=username, 
            has_password=bool(password),
            password_length=len(password) if password else 0
        )

        if not username or not password:
            duration = time.time() - start_time
            debug_logger.warning(
                "Login failed: missing credentials",
                username=username,
                has_password=bool(password),
                duration=duration
            )
            log_api_response(422, duration, error="Missing credentials")
            raise HTTPException(
                status_code=422, detail="Username and password are required"
            )

        # Authenticate user
        debug_logger.debug("Starting user authentication", username=username)
        user = await auth_service.authenticate_user(username, password, db)
        if not user:
            duration = time.time() - start_time
            metrics_service.record_api_request("POST", "/auth/login", 401, duration)
            debug_logger.warning(
                "Login failed: authentication failed",
                username=username,
                duration=duration,
            )
            log_api_response(401, duration, error="Authentication failed")
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not user.is_active:
            duration = time.time() - start_time
            metrics_service.record_api_request("POST", "/auth/login", 403, duration)
            debug_logger.warning(
                "Login failed: user account deactivated",
                username=username,
                user_id=str(user.id),
                duration=duration
            )
            log_api_response(403, duration, error="Account deactivated")
            raise HTTPException(status_code=403, detail="User account is deactivated")

        # Create token response
        debug_logger.debug("Creating token response", username=username, user_id=str(user.id))
        token_response = auth_service.create_token_response(user)

        duration = time.time() - start_time
        metrics_service.record_api_request("POST", "/auth/login", 200, duration)

        debug_logger.info(
            "User logged in successfully",
            username=username,
            user_id=str(user.id),
            duration=duration,
            client_ip=client_ip,
        )

        return token_response

    except HTTPException:
        duration = time.time() - start_time
        logger.warning(
            "Login failed with HTTP exception",
            username=username,
            duration=duration,
            client_ip=client_ip,
        )
        raise
    except Exception as e:
        duration = time.time() - start_time
        metrics_service.record_api_request("POST", "/auth/login", 500, duration)

        logger.error(
            "Login failed with internal error",
            username=username,
            error=str(e),
            duration=duration,
            client_ip=client_ip,
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/logout")
async def logout(request: Request):
    """
    User logout endpoint
    """
    start_time = time.time()

    try:
        # In a real implementation, you would invalidate the token
        # For now, we'll just return a success message

        duration = time.time() - start_time
        metrics_service.record_api_request("POST", "/auth/logout", 200, duration)

        logger.info("User logged out")

        return {"message": "Successfully logged out"}

    except Exception as e:
        duration = time.time() - start_time
        metrics_service.record_api_request("POST", "/auth/logout", 500, duration)

        logger.error("Logout failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/me")
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Get current user information
    """
    start_time = time.time()

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

        duration = time.time() - start_time
        metrics_service.record_api_request("GET", "/auth/me", 200, duration)

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": [role.name for role in user.roles],
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
        }

    except HTTPException:
        duration = time.time() - start_time
        metrics_service.record_api_request("GET", "/auth/me", 401, duration)
        raise
    except Exception as e:
        duration = time.time() - start_time
        metrics_service.record_api_request("GET", "/auth/me", 500, duration)

        logger.error("Failed to get current user", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/register")
async def register(user_data: dict, request: Request, db: Session = Depends(get_db)):
    """
    Register new user
    """
    start_time = time.time()

    try:
        username = user_data.get("username")
        email = user_data.get("email")
        password = user_data.get("password")
        roles = user_data.get("roles", ["user"])

        if not username or not email or not password:
            raise HTTPException(
                status_code=422, detail="Username, email and password are required"
            )

        # Create user
        user = await auth_service.create_user(username, email, password, roles, db)
        if not user:
            raise HTTPException(status_code=409, detail="Username already exists")

        duration = time.time() - start_time
        metrics_service.record_api_request("POST", "/auth/register", 201, duration)

        logger.info(
            "User registered successfully",
            username=username,
            email=email,
            user_id=user.id,
        )

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": [role.name for role in user.roles],
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }

    except HTTPException:
        duration = time.time() - start_time
        metrics_service.record_api_request("POST", "/auth/register", 422, duration)
        raise
    except Exception as e:
        duration = time.time() - start_time
        metrics_service.record_api_request("POST", "/auth/register", 500, duration)

        logger.error("User registration failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/change-password")
async def change_password(
    password_data: dict, request: Request, db: Session = Depends(get_db)
):
    """
    Change user password
    """
    start_time = time.time()

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

        # Validate current password
        current_password = password_data.get("current_password")
        new_password = password_data.get("new_password")

        if not current_password or not new_password:
            raise HTTPException(
                status_code=422, detail="Current password and new password are required"
            )

        if not auth_service.verify_password(current_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Current password is incorrect")

        # Update password
        success = await auth_service.update_user_password(user.id, new_password, db)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update password")

        duration = time.time() - start_time
        metrics_service.record_api_request(
            "POST", "/auth/change-password", 200, duration
        )

        logger.info("User password changed", username=username, user_id=user.id)

        return {"message": "Password changed successfully"}

    except HTTPException:
        duration = time.time() - start_time
        metrics_service.record_api_request(
            "POST", "/auth/change-password", 400, duration
        )
        raise
    except Exception as e:
        duration = time.time() - start_time
        metrics_service.record_api_request(
            "POST", "/auth/change-password", 500, duration
        )

        logger.error("Password change failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
