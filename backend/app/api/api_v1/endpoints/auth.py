"""
Authentication endpoints for SSO integration
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
import secrets
import json

from app.core.database import get_db
from app.core.sso import get_sso_provider, authenticate_user
from app.core.config import settings
from app.models.user import User
from app.utils.jwt import create_access_token
from app.models.schemas import TokenResponse, UserResponse

router = APIRouter()


@router.get("/login")
async def login(request: Request):
    """Initiate SSO login"""
    # Generate state parameter for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Store state in session or cache for validation
    # For simplicity, we'll use a simple approach here
    # In production, use Redis or database to store state
    
    provider = get_sso_provider()
    authorization_url = provider.get_authorization_url(state)
    
    return RedirectResponse(url=authorization_url)


@router.get("/callback")
async def callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Handle SSO callback"""
    try:
        # Validate state parameter (implement proper state validation)
        # For now, we'll skip state validation for simplicity
        
        provider = get_sso_provider()
        
        # Exchange code for token
        token_data = await provider.exchange_code_for_token(code)
        access_token = token_data.get('access_token')
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token received"
            )
        
        # Get user information
        user_info = await provider.get_user_info(access_token)
        
        # Authenticate user
        user = await authenticate_user(db, user_info)
        
        # Create JWT token
        jwt_token = create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        return TokenResponse(
            access_token=jwt_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
                is_active=user.is_active
            )
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/logout")
async def logout():
    """Logout user"""
    # In a real implementation, you might want to:
    # 1. Revoke the SSO token
    # 2. Blacklist the JWT token
    # 3. Clear session data
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_user_dependency)
):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active
    )


# Dependency for getting current user
async def get_current_user_dependency(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# OAuth2 scheme for JWT tokens
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/callback")
