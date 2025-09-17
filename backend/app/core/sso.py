"""
SSO authentication module for PTE-QR system
"""

from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User


class SSOProvider:
    """Base class for SSO providers"""

    def __init__(self):
        self.client_id = settings.SSO_CLIENT_ID
        self.client_secret = settings.SSO_CLIENT_SECRET
        self.redirect_uri = settings.SSO_REDIRECT_URI
        self.scope = settings.SSO_SCOPE

    def get_authorization_url(self, state: str) -> str:
        """Generate authorization URL for SSO login"""
        raise NotImplementedError

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        raise NotImplementedError

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from SSO provider"""
        raise NotImplementedError


class OAuth2SSOProvider(SSOProvider):
    """OAuth2 SSO provider implementation"""

    def __init__(self):
        super().__init__()
        self.authorization_url = settings.SSO_AUTHORIZATION_URL
        self.token_url = settings.SSO_TOKEN_URL
        self.userinfo_url = settings.SSO_USERINFO_URL

    def get_authorization_url(self, state: str) -> str:
        """Generate OAuth2 authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "response_type": "code",
            "state": state,
        }
        return f"{self.authorization_url}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.redirect_uri,
                    "code": code,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            return response.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from OAuth2 provider"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.userinfo_url, headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            return response.json()


class ThreeDPassportSSOProvider(SSOProvider):
    """3DPassport SSO provider implementation"""

    def __init__(self):
        super().__init__()
        self.authorization_url = settings.SSO_AUTHORIZATION_URL
        self.token_url = settings.SSO_TOKEN_URL
        self.userinfo_url = settings.SSO_USERINFO_URL

    def get_authorization_url(self, state: str) -> str:
        """Generate 3DPassport authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "response_type": "code",
            "state": state,
        }
        return f"{self.authorization_url}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.redirect_uri,
                    "code": code,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            return response.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from 3DPassport provider"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.userinfo_url, headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            return response.json()


def get_sso_provider() -> SSOProvider:
    """Get SSO provider based on configuration"""
    provider_type = settings.SSO_PROVIDER.lower()

    if provider_type == "oauth2":
        return OAuth2SSOProvider()
    elif provider_type == "3dpassport":
        return ThreeDPassportSSOProvider()
    else:
        raise ValueError(f"Unsupported SSO provider: {provider_type}")


async def authenticate_user(db: Session, user_info: Dict[str, Any]) -> User:
    """Authenticate user and create/update user record"""
    # Extract user information from SSO response
    username = (
        user_info.get("preferred_username")
        or user_info.get("username")
        or user_info.get("sub")
    )
    email = user_info.get("email")
    name = user_info.get("name") or user_info.get(
        "given_name", ""
    ) + " " + user_info.get("family_name", "")

    if not username:
        raise ValueError("Username not found in SSO response")

    # Check if user exists
    user = db.query(User).filter(User.username == username).first()

    if user:
        # Update existing user
        user.email = email or user.email
        user.full_name = name.strip() or user.full_name
        user.is_active = True
    else:
        # Create new user
        user = User(
            username=username,
            email=email,
            full_name=name.strip(),
            role="employee",  # Default role
            is_active=True,
        )
        db.add(user)

    db.commit()
    db.refresh(user)
    return user


async def get_user_by_token(db: Session, access_token: str) -> Optional[User]:
    """Get user by access token"""
    try:
        provider = get_sso_provider()
        user_info = await provider.get_user_info(access_token)
        return await authenticate_user(db, user_info)
    except Exception:
        return None
