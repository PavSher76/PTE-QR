"""
Authentication service
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import jwt
import structlog
from passlib.context import CryptContext

from app.core.config import settings
from app.models.user import User, UserRole

logger = structlog.get_logger()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service"""

    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)

    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )

        to_encode.update({"exp": int(expire.timestamp())})

        # Ensure all values are JSON serializable
        for key, value in to_encode.items():
            if hasattr(value, "__str__") and not isinstance(
                value, (str, int, float, bool, list, dict)
            ):
                logger.warning(
                    f"Converting non-serializable value for key '{key}': "
                    f"{type(value)} -> {str(value)}"
                )
                to_encode[key] = str(value)

        logger.info(f"JWT payload: {to_encode}")
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning("Token verification failed", error=str(e))
            return None

    async def authenticate_user(
        self, username: str, password: str, db
    ) -> Optional[User]:
        """Authenticate user with username and password"""
        logger.info("Starting user authentication", username=username)

        try:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                logger.warning("User not found", username=username)
                return None

            logger.info(
                "User found, verifying password",
                username=username,
                user_id=str(user.id),
            )

            if not self.verify_password(password, user.hashed_password):
                logger.warning("Invalid password for user", username=username)
                return None

            logger.info(
                "User authentication successful",
                username=username,
                user_id=str(user.id),
            )
            return user
        except Exception as e:
            logger.error(
                "User authentication failed",
                username=username,
                error=str(e),
                exc_info=True,
            )
            return None

    async def create_user(
        self, username: str, email: str, password: str, roles: List[str] = None, db=None
    ) -> Optional[User]:
        """Create new user"""
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(User.username == username).first()
            if existing_user:
                return None

            # Hash password
            hashed_password = self.get_password_hash(password)

            # Create user
            user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                is_active=True,
            )

            db.add(user)
            db.commit()
            db.refresh(user)

            # Add roles
            if roles:
                for role_name in roles:
                    role = db.query(UserRole).filter(UserRole.name == role_name).first()
                    if role:
                        user.roles.append(role)

                db.commit()

            logger.info("User created", username=username, email=email)
            return user

        except Exception as e:
            logger.error("User creation failed", username=username, error=str(e))
            return None

    async def get_user_by_username(self, username: str, db) -> Optional[User]:
        """Get user by username"""
        try:
            return db.query(User).filter(User.username == username).first()
        except Exception as e:
            logger.error(
                "Failed to get user by username", username=username, error=str(e)
            )
            return None

    async def get_user_by_id(self, user_id: int, db) -> Optional[User]:
        """Get user by ID"""
        try:
            return db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error("Failed to get user by ID", user_id=user_id, error=str(e))
            return None

    async def update_user_password(self, user_id: int, new_password: str, db) -> bool:
        """Update user password"""
        try:
            user = await self.get_user_by_id(user_id, db)
            if not user:
                return False

            user.hashed_password = self.get_password_hash(new_password)
            db.commit()

            logger.info("User password updated", user_id=user_id)
            return True

        except Exception as e:
            logger.error(
                "Failed to update user password", user_id=user_id, error=str(e)
            )
            return False

    async def deactivate_user(self, user_id: int, db) -> bool:
        """Deactivate user"""
        try:
            user = await self.get_user_by_id(user_id, db)
            if not user:
                return False

            user.is_active = False
            db.commit()

            logger.info("User deactivated", user_id=user_id)
            return True

        except Exception as e:
            logger.error("Failed to deactivate user", user_id=user_id, error=str(e))
            return False

    def has_role(self, user: User, role_name: str) -> bool:
        """Check if user has specific role"""
        return any(role.name == role_name for role in user.roles)

    def has_any_role(self, user: User, role_names: List[str]) -> bool:
        """Check if user has any of the specified roles"""
        user_roles = {role.name for role in user.roles}
        return bool(user_roles.intersection(set(role_names)))

    async def get_user_permissions(self, user: User) -> List[str]:
        """Get user permissions based on roles"""
        permissions = set()

        for role in user.roles:
            permissions.update(role.permissions)

        return list(permissions)

    def create_token_response(self, user: User) -> Dict[str, Any]:
        """Create token response for user"""
        access_token_expires = timedelta(minutes=self.access_token_expire_minutes)

        # Debug: log the data being passed to create_access_token
        token_data = {"sub": user.username, "user_id": str(user.id)}
        logger.info(f"Creating token for user: {user.username}, data: {token_data}")

        access_token = self.create_access_token(
            data=token_data, expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60,
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "roles": [str(role.name) for role in user.roles] if user.roles else [],
                "is_active": user.is_active,
            },
        }


# Global auth service instance - will be created lazily
_auth_service_instance = None

def get_auth_service() -> AuthService:
    """Get auth service instance (lazy initialization)"""
    global _auth_service_instance
    if _auth_service_instance is None:
        _auth_service_instance = AuthService()
    return _auth_service_instance

# For backward compatibility
auth_service = get_auth_service()
