"""
FastAPI Dependencies
====================
Dependency injection functions for FastAPI routes.
Handles authentication, authorization, and common dependencies.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from commons.security import verify_access_token
from database.database import get_engine
from models.user_model import User

# HTTP Bearer token scheme for Swagger UI
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    FastAPI dependency to get the current authenticated user.

    Extracts and validates the JWT token from the Authorization header,
    then fetches the user from the database.

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        User object for the authenticated user

    Raises:
        HTTPException 401: If token is invalid or expired
        HTTPException 401: If user not found in database
        HTTPException 403: If user account is deactivated

    Example usage in route:
        @router.get("/me")
        async def get_profile(current_user: User = Depends(get_current_user)):
            return current_user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    # Verify the token
    payload = verify_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("user_id")
    if user_id is None:
        raise credentials_exception

    # Get user from database
    engine = get_engine()
    from bson import ObjectId

    try:
        user = await engine.find_one(User, User.id == ObjectId(user_id))
    except Exception:
        raise credentials_exception

    if user is None:
        raise credentials_exception

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is deactivated"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency that ensures the user is active.

    This is an alias for get_current_user since it already checks is_active.
    Kept for semantic clarity in routes.
    """
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[User]:
    """
    Optional authentication dependency.

    Returns the user if authenticated, None otherwise.
    Useful for routes that work differently for authenticated vs anonymous users.

    Example usage:
        @router.get("/items")
        async def get_items(user: Optional[User] = Depends(get_optional_user)):
            if user:
                return get_user_items(user.id)
            return get_public_items()
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_role(allowed_roles: list[str]):
    """
    Dependency factory for role-based access control.

    Args:
        allowed_roles: List of roles that are allowed access

    Returns:
        Dependency function that validates user role

    Example usage:
        @router.post("/services")
        async def create_service(
            current_user: User = Depends(require_role(["cleaner"]))
        ):
            # Only cleaners can create services
            pass
    """

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.value not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker


# Convenience dependencies for specific roles
require_customer = require_role(["customer"])
require_cleaner = require_role(["cleaner"])
require_any_role = require_role(["customer", "cleaner"])
