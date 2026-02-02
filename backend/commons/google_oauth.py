"""
Google OAuth Service
====================
Handles Google OAuth 2.0 authentication flow.
Provides utilities to:
- Generate Google OAuth URL
- Exchange authorization code for tokens
- Fetch user information from Google
"""

import os
import httpx
from typing import Dict, Any, Optional
from urllib.parse import urlencode
from dotenv import load_dotenv

from commons.logger import logger

# Load environment variables
load_dotenv()

# Initialize logger
log = logger(__name__)

# =============================================================================
# Configuration
# =============================================================================

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback"
)

# Google OAuth endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# Scopes to request
GOOGLE_SCOPES = [
    "openid",
    "email",
    "profile",
]


# =============================================================================
# OAuth URL Generation
# =============================================================================


def get_google_oauth_url(state: Optional[str] = None) -> str:
    """
    Generate the Google OAuth authorization URL.

    Args:
        state: Optional state parameter for CSRF protection

    Returns:
        The full Google OAuth URL to redirect users to

    Example:
        >>> url = get_google_oauth_url()
        >>> # Redirect user to this URL
    """
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(GOOGLE_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    }

    if state:
        params["state"] = state

    url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    log.info("Generated Google OAuth URL")
    return url


# =============================================================================
# Token Exchange
# =============================================================================


async def exchange_code_for_tokens(code: str) -> Optional[Dict[str, Any]]:
    """
    Exchange authorization code for access and refresh tokens.

    Args:
        code: The authorization code from Google's redirect

    Returns:
        Dictionary containing access_token, refresh_token, etc.
        Returns None if exchange fails

    Example:
        >>> tokens = await exchange_code_for_tokens(auth_code)
        >>> if tokens:
        ...     access_token = tokens["access_token"]
    """
    log.info("Exchanging authorization code for tokens")
    log.info(f"Using redirect_uri: {GOOGLE_REDIRECT_URI}")

    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            if response.status_code != 200:
                log.error(f"Token exchange failed with status {response.status_code}")
                log.error(f"Response: {response.text}")
                log.error(
                    f"Request data (without secret): code={code[:20]}..., client_id={GOOGLE_CLIENT_ID}, redirect_uri={GOOGLE_REDIRECT_URI}"
                )
                return None

            tokens = response.json()
            log.info("Successfully exchanged code for tokens")
            return tokens

    except Exception as e:
        log.error(f"Error exchanging code for tokens: {str(e)}")
        return None


# =============================================================================
# User Info Retrieval
# =============================================================================


async def get_google_user_info(access_token: str) -> Optional[Dict[str, Any]]:
    """
    Fetch user information from Google using the access token.

    Args:
        access_token: The access token from Google

    Returns:
        Dictionary containing user info (id, email, name, picture, etc.)
        Returns None if fetch fails

    Example:
        >>> user_info = await get_google_user_info(access_token)
        >>> if user_info:
        ...     email = user_info["email"]
        ...     name = user_info["name"]
    """
    log.info("Fetching user info from Google")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code != 200:
                log.error(f"Failed to fetch user info: {response.text}")
                return None

            user_info = response.json()
            log.info(
                f"Successfully fetched Google user info for: {user_info.get('email')}"
            )
            return user_info

    except Exception as e:
        log.error(f"Error fetching Google user info: {str(e)}")
        return None


# =============================================================================
# Helper Functions
# =============================================================================


def is_google_oauth_configured() -> bool:
    """
    Check if Google OAuth is properly configured.

    Returns:
        True if all required configuration is present
    """
    return bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)


async def verify_google_token(access_token: str) -> bool:
    """
    Verify a Google access token is valid.

    Args:
        access_token: The Google access token to verify

    Returns:
        True if token is valid, False otherwise
    """
    user_info = await get_google_user_info(access_token)
    return user_info is not None
