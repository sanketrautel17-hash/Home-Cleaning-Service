"""
Security Utilities
==================
Centralized security functions for the Home Cleaning Service API.
Includes password hashing (bcrypt) and JWT token management.

Based on project documentation requirements:
- Access Token: 30 minutes expiry
- Refresh Token: 7 days expiry
- Password: Bcrypt with cost factor 12
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import jwt, JWTError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================================================
# Configuration
# =============================================================================

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "60"))

# Password hashing context with bcrypt (cost factor 12 as per documentation)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # ~250ms computation time for brute-force resistance
)


# =============================================================================
# Password Utilities
# =============================================================================


def hash_password(plain_password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        plain_password: The plain text password to hash

    Returns:
        The hashed password string

    Example:
        >>> hashed = hash_password("SecurePass123!")
        >>> print(hashed)
        '$2b$12$...'
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against its hash.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against

    Returns:
        True if password matches, False otherwise

    Example:
        >>> hashed = hash_password("SecurePass123!")
        >>> verify_password("SecurePass123!", hashed)
        True
        >>> verify_password("WrongPassword", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


# =============================================================================
# JWT Token Utilities
# =============================================================================


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data to encode in the token (typically user_id, role)
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT access token string

    Example:
        >>> token = create_access_token({"user_id": "123", "role": "customer"})
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "access"})

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token (long-lived).

    Args:
        data: Payload data to encode (typically just user_id)
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT refresh token string

    Example:
        >>> token = create_refresh_token({"user_id": "123"})
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_tokens(user_id: str, role: str) -> Dict[str, Any]:
    """
    Create both access and refresh tokens for a user.

    Args:
        user_id: The user's unique identifier
        role: The user's role (customer/cleaner)

    Returns:
        Dictionary with access_token, refresh_token, token_type, and expires_in

    Example:
        >>> tokens = create_tokens("507f1f77bcf86cd799439011", "customer")
        >>> print(tokens["access_token"])
    """
    access_token = create_access_token({"user_id": user_id, "role": role})

    refresh_token = create_refresh_token({"user_id": user_id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # in seconds
    }


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.

    Args:
        token: The JWT token string to decode

    Returns:
        Decoded payload if valid, None if invalid or expired

    Example:
        >>> payload = decode_token(access_token)
        >>> if payload:
        >>>     print(payload["user_id"])
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify an access token and return its payload.

    Args:
        token: The access token to verify

    Returns:
        Decoded payload if valid access token, None otherwise
    """
    payload = decode_token(token)
    if payload and payload.get("type") == "access":
        return payload
    return None


def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify a refresh token and return its payload.

    Args:
        token: The refresh token to verify

    Returns:
        Decoded payload if valid refresh token, None otherwise
    """
    payload = decode_token(token)
    if payload and payload.get("type") == "refresh":
        return payload
    return None


# =============================================================================
# Password Reset Token Utilities
# =============================================================================


def create_reset_token(email: str) -> str:
    """
    Create a password reset token.

    Args:
        email: User's email address

    Returns:
        JWT token for password reset (valid for RESET_TOKEN_EXPIRE_MINUTES)

    Example:
        >>> token = create_reset_token("user@example.com")
    """
    expire = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "reset",
    }

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token and extract the email.

    Args:
        token: The reset token to verify

    Returns:
        Email address if valid, None if invalid or expired

    Example:
        >>> email = verify_reset_token(reset_token)
        >>> if email:
        >>>     print(f"Reset password for: {email}")
    """
    payload = decode_token(token)
    if payload and payload.get("type") == "reset":
        return payload.get("email")
    return None


# =============================================================================
# Email Verification Token Utilities
# =============================================================================


def create_email_verification_token(email: str) -> str:
    """
    Create an email verification token.

    Args:
        email: User's email address

    Returns:
        JWT token for email verification (valid for 24 hours)
    """
    expire = datetime.utcnow() + timedelta(hours=24)

    to_encode = {
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "email_verify",
    }

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_email_verification_token(token: str) -> Optional[str]:
    """
    Verify an email verification token and extract the email.

    Args:
        token: The email verification token

    Returns:
        Email address if valid, None if invalid or expired
    """
    payload = decode_token(token)
    if payload and payload.get("type") == "email_verify":
        return payload.get("email")
    return None
