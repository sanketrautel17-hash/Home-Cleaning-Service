import time
import jwt
import os
from passlib.context import CryptContext
from fastapi import HTTPException, status
from dotenv import load_dotenv


load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.environ.get("secret")
JWT_ALGORITHM = os.environ.get("algorithm")


def signJWT(
    id: str,
    expiry_duration: int = 3600,
    status: str = "ACTIVE",
):
    """
    Sign a JWT token with user role, id, expiry duration, and status.
    """
    if not JWT_SECRET or not JWT_ALGORITHM:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT secret or algorithm not configured",
        )

    payload = {
        "id": id,
        "status": status,
        "expires": time.time() + expiry_duration,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def encodeJWT(payload: dict = {}, expiry_duration: int = 3600):
    """
    Encode a JWT token with a given payload.
    """
    if not JWT_SECRET or not JWT_ALGORITHM:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT secret or algorithm not configured",
        )

    payload_copy = dict(payload) if payload else {}
    payload_copy["expires"] = time.time() + expiry_duration
    token = jwt.encode(payload_copy, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decodeJWT(token: str):
    """
    Decode a JWT token to extract user role, id, status, and expiry time.
    """
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token.get("expires") > time.time() else None
    except Exception:
        return None


def encrypt_password(password: str) -> str:
    """
    Encrypt a plain password using bcrypt hashing.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if the provided plain password matches the hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


def encode_reset_password_token(email: str, expiry_duration: int = 300) -> str:
    """
    Encode a reset password token with the user's email.
    """
    if not JWT_SECRET or not JWT_ALGORITHM:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT secret or algorithm not configured",
        )

    payload = {"email": email, "expires": time.time() + expiry_duration}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


# payload = {"otp": "1234"}

# encodeJWT(payload, expiry_duration=600)
