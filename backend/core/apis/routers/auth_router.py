"""
Auth Router
===========
FastAPI routes for authentication endpoints.
All routes are prefixed with /api/auth

Endpoints:
- POST /register     - Create new user account
- POST /login        - Authenticate and get tokens
- POST /refresh      - Refresh access token
- POST /forgot-password - Request password reset
- POST /reset-password  - Reset password with token
- POST /change-password - Change password (authenticated)
- GET  /me           - Get current user profile
- POST /verify-email - Verify email address
- POST /send-verification - Resend verification email
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from controllers.auth_controller import auth_controller
from commons.dependencies import get_current_user
from models.user_model import User
from core.apis.schemas.requests.auth_request import (
    UserRegisterRequest,
    UserLoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    RefreshTokenRequest,
    ChangePasswordRequest,
)
from core.apis.schemas.responses.auth_response import (
    TokenResponse,
    UserResponse,
    UserWithTokenResponse,
    MessageResponse,
)

# Create router with prefix and tags
router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    },
)


# =============================================================================
# REGISTRATION
# =============================================================================


@router.post(
    "/register",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email, password, and profile info.",
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "id": "507f1f77bcf86cd799439011",
                            "email": "user@example.com",
                            "full_name": "John Doe",
                            "role": "customer",
                        },
                        "tokens": {
                            "access_token": "eyJhbGci...",
                            "refresh_token": "eyJhbGci...",
                            "token_type": "bearer",
                            "expires_in": 1800,
                        },
                        "message": "Registration successful",
                    }
                }
            },
        },
        400: {"description": "Email already exists or validation error"},
    },
)
async def register(request: UserRegisterRequest):
    """
    Register a new user account.

    - **email**: Valid email address (must be unique)
    - **password**: Strong password (min 8 chars, uppercase, lowercase, number, special char)
    - **full_name**: User's full name
    - **role**: Either 'customer' or 'cleaner'
    - **phone**: Optional phone number
    """
    result = await auth_controller.register(
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        role=request.role,
        phone=request.phone,
    )

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)


# =============================================================================
# LOGIN
# =============================================================================


@router.post(
    "/login",
    response_model=None,
    summary="User login",
    description="Authenticate with email and password to receive JWT tokens.",
    responses={
        200: {
            "description": "Login successful",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "id": "507f1f77bcf86cd799439011",
                            "email": "user@example.com",
                            "full_name": "John Doe",
                            "role": "customer",
                        },
                        "tokens": {
                            "access_token": "eyJhbGci...",
                            "refresh_token": "eyJhbGci...",
                            "token_type": "bearer",
                            "expires_in": 1800,
                        },
                        "message": "Login successful",
                    }
                }
            },
        },
        401: {"description": "Invalid email or password"},
    },
)
async def login(request: UserLoginRequest):
    """
    Authenticate user and receive tokens.

    - **email**: Registered email address
    - **password**: User's password

    Returns access token (30 min) and refresh token (7 days).
    """
    result = await auth_controller.login(
        email=request.email,
        password=request.password,
    )

    return result


# =============================================================================
# TOKEN REFRESH
# =============================================================================


@router.post(
    "/refresh",
    response_model=None,
    summary="Refresh access token",
    description="Get new access token using a valid refresh token.",
    responses={
        200: {
            "description": "Token refreshed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "tokens": {
                            "access_token": "eyJhbGci...",
                            "refresh_token": "eyJhbGci...",
                            "token_type": "bearer",
                            "expires_in": 1800,
                        },
                        "message": "Token refreshed successfully",
                    }
                }
            },
        },
        401: {"description": "Invalid or expired refresh token"},
    },
)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token.

    Use the refresh token to get a new access token when the old one expires.

    - **refresh_token**: Valid refresh token from login
    """
    result = await auth_controller.refresh_token(refresh_token=request.refresh_token)

    return result


# =============================================================================
# FORGOT PASSWORD
# =============================================================================


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Request password reset",
    description="Send password reset email (returns token in dev mode).",
    responses={
        200: {
            "description": "Reset email sent (if account exists)",
            "content": {
                "application/json": {
                    "example": {
                        "message": "If the email exists, a reset link has been sent",
                        "success": True,
                    }
                }
            },
        }
    },
)
async def forgot_password(request: ForgotPasswordRequest):
    """
    Request password reset.

    Initiates the password reset flow by sending a reset token.
    For security, always returns success regardless of whether email exists.

    - **email**: Email address to send reset link
    """
    result = await auth_controller.forgot_password(email=request.email)

    return result


# =============================================================================
# RESET PASSWORD
# =============================================================================


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password",
    description="Reset password using the token from forgot-password.",
    responses={
        200: {
            "description": "Password reset successful",
            "content": {
                "application/json": {
                    "example": {"message": "Password reset successful", "success": True}
                }
            },
        },
        400: {"description": "Invalid or expired reset token"},
    },
)
async def reset_password(request: ResetPasswordRequest):
    """
    Reset password with token.

    Complete the password reset using the token received via email.

    - **token**: Reset token from forgot-password email
    - **new_password**: New password (must meet strength requirements)
    """
    result = await auth_controller.reset_password(
        token=request.token,
        new_password=request.new_password,
    )

    return result


# =============================================================================
# CHANGE PASSWORD (Authenticated)
# =============================================================================


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change password",
    description="Change password for authenticated user.",
    responses={
        200: {
            "description": "Password changed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Password changed successfully",
                        "success": True,
                    }
                }
            },
        },
        400: {"description": "Current password is incorrect"},
        401: {"description": "Not authenticated"},
    },
)
async def change_password(
    request: ChangePasswordRequest, current_user: User = Depends(get_current_user)
):
    """
    Change password (requires authentication).

    Allows authenticated users to change their password.

    - **current_password**: Current password for verification
    - **new_password**: New password (must meet strength requirements)
    """
    result = await auth_controller.change_password(
        user_id=str(current_user.id),
        current_password=request.current_password,
        new_password=request.new_password,
    )

    return result


# =============================================================================
# GET CURRENT USER
# =============================================================================


@router.get(
    "/me",
    response_model=None,
    summary="Get current user",
    description="Get profile of the currently authenticated user.",
    responses={
        200: {
            "description": "Current user profile",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "id": "507f1f77bcf86cd799439011",
                            "email": "user@example.com",
                            "full_name": "John Doe",
                            "phone": "+919876543210",
                            "role": "customer",
                            "profile_pic": None,
                            "is_active": True,
                            "email_verified": False,
                            "created_at": "2026-01-31T12:00:00",
                            "updated_at": "2026-01-31T12:00:00",
                        }
                    }
                }
            },
        },
        401: {"description": "Not authenticated"},
    },
)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current user profile.

    Returns the profile of the authenticated user.
    Requires valid access token in Authorization header.
    """
    result = await auth_controller.get_me(user=current_user)

    return result


# =============================================================================
# EMAIL VERIFICATION
# =============================================================================


@router.post(
    "/verify-email",
    response_model=MessageResponse,
    summary="Verify email",
    description="Verify email address using verification token.",
    responses={
        200: {
            "description": "Email verified successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Email verified successfully",
                        "success": True,
                    }
                }
            },
        },
        400: {"description": "Invalid or expired verification token"},
    },
)
async def verify_email(token: str):
    """
    Verify email address.

    Complete email verification using the token from verification email.

    - **token**: Verification token from email
    """
    result = await auth_controller.verify_email(token=token)

    return result


@router.post(
    "/send-verification",
    response_model=None,
    summary="Resend verification email",
    description="Resend email verification link.",
    responses={
        200: {
            "description": "Verification email sent",
            "content": {
                "application/json": {
                    "example": {"message": "Verification email sent", "success": True}
                }
            },
        },
        404: {"description": "User not found"},
    },
)
async def send_verification_email(current_user: User = Depends(get_current_user)):
    """
    Resend verification email.

    Request a new email verification link.
    Requires authentication.
    """
    result = await auth_controller.send_verification_email(email=current_user.email)

    return result


# =============================================================================
# GOOGLE OAUTH
# =============================================================================


@router.get(
    "/google/login",
    response_model=None,
    summary="Get Google OAuth login URL",
    description="Get the Google OAuth URL to redirect users for login.",
    responses={
        200: {
            "description": "Google OAuth URL",
            "content": {
                "application/json": {
                    "example": {
                        "url": "https://accounts.google.com/o/oauth2/v2/auth?...",
                        "message": "Redirect user to this URL for Google login",
                    }
                }
            },
        },
        500: {"description": "Google OAuth not configured"},
    },
)
async def google_login(state: str = None):
    """
    Get Google OAuth login URL.

    Frontend should redirect users to the returned URL.
    After authentication, Google will redirect to the callback endpoint.

    - **state**: Optional state parameter for CSRF protection
    """
    result = await auth_controller.get_google_login_url(state=state)

    return result


@router.get(
    "/google/callback",
    response_model=None,
    summary="Google OAuth callback",
    description="Handle the OAuth callback from Google and authenticate user.",
    responses={
        200: {
            "description": "Google login successful",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "id": "507f1f77bcf86cd799439011",
                            "email": "user@gmail.com",
                            "full_name": "John Doe",
                            "role": "customer",
                            "auth_provider": "google",
                        },
                        "tokens": {
                            "access_token": "eyJhbGci...",
                            "refresh_token": "eyJhbGci...",
                            "token_type": "bearer",
                            "expires_in": 1800,
                        },
                        "message": "Google login successful",
                    }
                }
            },
        },
        400: {"description": "Failed to authenticate with Google"},
        403: {"description": "Account is deactivated"},
    },
)
async def google_callback(code: str, state: str = None, role: str = "customer"):
    """
    Handle Google OAuth callback.

    This endpoint is called by Google after user authentication.
    It exchanges the authorization code for tokens and creates/logs in the user.

    - **code**: Authorization code from Google
    - **state**: State parameter for CSRF verification (if provided during login)
    - **role**: User role for new accounts ('customer' or 'cleaner')
    """
    result = await auth_controller.google_callback(code=code, role=role)

    return result
