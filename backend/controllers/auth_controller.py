"""
Auth Controller
===============
Business logic for authentication operations.
Orchestrates between routes, CRUD operations, and security utilities.

Handles:
- User registration
- User login
- Token refresh
- Password reset flow
- Email verification
- Password change
"""

import json
from typing import Dict, Any, Optional
from fastapi import HTTPException, status

from cruds.user_crud import user_crud
from commons.security import (
    create_tokens,
    verify_refresh_token,
    create_reset_token,
    verify_reset_token,
    create_email_verification_token,
    verify_email_verification_token,
    verify_password,
    hash_password,
)
from commons.logger import logger
from commons.mail import send_verification_link
from models.user_model import User

# Initialize logger
log = logger(__name__)


class AuthController:
    """
    Authentication business logic controller.

    This class contains all authentication-related business logic,
    separating it from route handlers for better maintainability.

    Usage:
        auth_controller = AuthController()
        result = await auth_controller.register(...)
    """

    # =========================================================================
    # REGISTRATION
    # =========================================================================

    async def register(
        self,
        email: str,
        password: str,
        full_name: str,
        role: str = "customer",
        phone: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Register a new user.

        Args:
            email: User's email address
            password: Plain text password (already validated by schema)
            full_name: User's full name
            role: User role ('customer' or 'cleaner')
            phone: Optional phone number

        Returns:
            Dictionary containing user data and tokens

        Raises:
            HTTPException 400: If email already exists
            HTTPException 500: If registration fails
        """
        log.info(f"Attempting to register user: {email}")

        try:
            # Create user (CRUD handles password hashing)
            user = await user_crud.create_user(
                email=email,
                password=password,
                full_name=full_name,
                role=role,
                phone=phone,
            )

            log.info(f"User registered successfully: {email}")

            # Send verification email
            try:
                # Generate verification token
                token = create_email_verification_token(email)
                # Send email
                await send_verification_link(email, token)
                log.info(f"Verification email sent to: {email}")
            except Exception as e:
                log.error(f"Failed to send verification email to {email}: {str(e)}")
                # Continue, but user might need to request resend

            # Build response (No tokens returned - user must verify email)
            return {
                "message": "Registration successful. Please check your email to verify your account.",
                "success": True,
            }

        except ValueError as e:
            log.warning(f"Registration failed for {email}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            log.error(f"Registration error for {email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred during registration",
            )

    # =========================================================================
    # LOGIN
    # =========================================================================

    async def login(
        self,
        email: str,
        password: str,
    ) -> Dict[str, Any]:
        """
        Authenticate user and return tokens.

        Args:
            email: User's email address
            password: Plain text password

        Returns:
            Dictionary containing user data and tokens

        Raises:
            HTTPException 401: If credentials are invalid
            HTTPException 403: If account is deactivated
        """
        log.info(f"Login attempt for: {email}")

        # Authenticate user
        user = await user_crud.authenticate_user(email, password)

        if not user:
            log.warning(f"Login failed for: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            log.warning(f"Login attempt for deactivated account: {email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated"
            )

        if not user.email_verified:
            log.warning(f"Login attempt for unverified email: {email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email not verified. Please check your inbox.",
            )

        log.info(f"Login successful for: {email}")

        # Create tokens
        tokens = create_tokens(user_id=str(user.id), role=user.role.value)

        return {
            "user": self._user_to_dict(user),
            "tokens": tokens,
            "message": "Login successful",
        }

    # =========================================================================
    # TOKEN REFRESH
    # =========================================================================

    async def refresh_token(
        self,
        refresh_token: str,
    ) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            Dictionary containing new tokens

        Raises:
            HTTPException 401: If refresh token is invalid or expired
        """
        log.info("Token refresh attempt")

        # Verify refresh token
        payload = verify_refresh_token(refresh_token)

        if not payload:
            log.warning("Invalid refresh token provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("user_id")

        # Get user to verify still exists and is active
        user = await user_crud.get_user_by_id(user_id)

        if not user:
            log.warning(f"User not found for refresh: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        if not user.is_active:
            log.warning(f"Refresh attempt for deactivated: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated"
            )

        log.info(f"Token refreshed for user: {user_id}")

        # Create new tokens
        tokens = create_tokens(user_id=str(user.id), role=user.role.value)

        return {"tokens": tokens, "message": "Token refreshed successfully"}

    # =========================================================================
    # FORGOT PASSWORD
    # =========================================================================

    async def forgot_password(
        self,
        email: str,
    ) -> Dict[str, Any]:
        """
        Initiate password reset flow.

        Generates a reset token. In production, this would send an email.
        For development, returns the token directly.

        Args:
            email: User's email address

        Returns:
            Dictionary with success message (and token in dev mode)

        Note:
            Always returns success to prevent email enumeration attacks.
        """
        log.info(f"Password reset requested for: {email}")

        # Check if user exists
        user = await user_crud.get_user_by_email(email)

        if user:
            # Generate reset token
            reset_token = create_reset_token(email)

            log.info(f"Reset token generated for: {email}")

            # TODO: In production, send email with reset link
            # For now, return token directly for testing
            return {
                "message": "If the email exists, a reset link has been sent",
                "success": True,
                # Include token for development/testing only
                "reset_token": reset_token,  # Remove in production!
            }

        # Return same message even if user doesn't exist (security)
        return {
            "message": "If the email exists, a reset link has been sent",
            "success": True,
        }

    # =========================================================================
    # RESET PASSWORD
    # =========================================================================

    async def reset_password(
        self,
        token: str,
        new_password: str,
    ) -> Dict[str, Any]:
        """
        Reset password using reset token.

        Args:
            token: Password reset token
            new_password: New password (already validated by schema)

        Returns:
            Dictionary with success message

        Raises:
            HTTPException 400: If token is invalid or expired
            HTTPException 404: If user not found
        """
        log.info("Password reset attempt")

        # Verify reset token
        email = verify_reset_token(token)

        if not email:
            log.warning("Invalid reset token provided")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        # Update password
        success = await user_crud.update_password_by_email(email, new_password)

        if not success:
            log.warning(f"User not found for password reset: {email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        log.info(f"Password reset successful for: {email}")

        return {"message": "Password reset successful", "success": True}

    # =========================================================================
    # CHANGE PASSWORD (Authenticated)
    # =========================================================================

    async def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str,
    ) -> Dict[str, Any]:
        """
        Change password for authenticated user.

        Args:
            user_id: Current user's ID
            current_password: Current password for verification
            new_password: New password (already validated by schema)

        Returns:
            Dictionary with success message

        Raises:
            HTTPException 400: If current password is wrong
            HTTPException 404: If user not found
        """
        log.info(f"Password change attempt for user: {user_id}")

        # Verify current password
        is_valid = await user_crud.verify_current_password(user_id, current_password)

        if not is_valid:
            log.warning(f"Wrong current password for: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        # Update password
        success = await user_crud.update_password(user_id, new_password)

        if not success:
            log.error(f"Password update failed for: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        log.info(f"Password changed successfully for: {user_id}")

        return {"message": "Password changed successfully", "success": True}

    # =========================================================================
    # EMAIL VERIFICATION
    # =========================================================================

    async def send_verification_email(
        self,
        email: str,
    ) -> Dict[str, Any]:
        """
        Send email verification link.

        Args:
            email: User's email address

        Returns:
            Dictionary with token (for dev) and success message
        """
        log.info(f"Verification email requested for: {email}")

        user = await user_crud.get_user_by_email(email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if user.email_verified:
            return {"message": "Email is already verified", "success": True}

        # Generate verification token
        token = create_email_verification_token(email)

        # Send actual email
        await send_verification_link(email, token)
        log.info(f"Verification token generated and sent for: {email}")

        return {
            "message": "Verification email sent",
            "success": True,
        }

    async def verify_email(
        self,
        token: str,
    ) -> Dict[str, Any]:
        """
        Verify user's email address.

        Args:
            token: Email verification token

        Returns:
            Dictionary with success message

        Raises:
            HTTPException 400: If token is invalid
        """
        log.info("Email verification attempt")

        # Verify token
        email = verify_email_verification_token(token)

        if not email:
            log.warning("Invalid email verification token")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token",
            )

        # Mark email as verified
        success = await user_crud.verify_user_email(email)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        log.info(f"Email verified for: {email}")

        return {"message": "Email verified successfully", "success": True}

    # =========================================================================
    # GET CURRENT USER
    # =========================================================================

    async def get_me(self, user: User) -> Dict[str, Any]:
        """
        Get current user profile.

        Args:
            user: Current authenticated user

        Returns:
            Dictionary with user data
        """
        return {"user": self._user_to_dict(user)}

    # =========================================================================
    # GOOGLE OAUTH
    # =========================================================================

    async def get_google_login_url(self, state: Optional[str] = None) -> Dict[str, Any]:
        """
        Get Google OAuth login URL.

        Args:
            state: Optional state parameter for CSRF protection

        Returns:
            Dictionary with Google OAuth URL

        Raises:
            HTTPException 500: If Google OAuth is not configured
        """
        from commons.google_oauth import (
            get_google_oauth_url,
            is_google_oauth_configured,
        )

        if not is_google_oauth_configured():
            log.error("Google OAuth not configured")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google OAuth is not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.",
            )

        url = get_google_oauth_url(state)

        return {"url": url, "message": "Redirect user to this URL for Google login"}

    async def google_callback(
        self,
        code: str,
        state: Optional[str] = None,
        role: str = "customer",
    ) -> Dict[str, Any]:
        """
        Handle Google OAuth callback.

        Exchange the authorization code for tokens, fetch user info,
        and create or login the user.

        Args:
            code: Authorization code from Google
            state: State parameter containing intent (login/register)
            role: User role for new users ('customer' or 'cleaner')

        Returns:
            Dictionary containing user data and tokens

        Raises:
            HTTPException 400: If code exchange fails
            HTTPException 403: If account is deactivated
        """
        from commons.google_oauth import exchange_code_for_tokens, get_google_user_info

        log.info("Processing Google OAuth callback")

        # Parse state for intent
        intent = "register"  # Default behavior
        if state:
            try:
                state_data = json.loads(state)
                if isinstance(state_data, dict):
                    intent = state_data.get("intent", "register")
                    if "role" in state_data:
                        role = state_data["role"]
            except (json.JSONDecodeError, TypeError):
                # If state is not JSON, ignore it
                pass

        # Exchange code for tokens
        google_tokens = await exchange_code_for_tokens(code)

        if not google_tokens:
            log.error("Failed to exchange authorization code")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to authenticate with Google. Please try again.",
            )

        access_token = google_tokens.get("access_token")

        # Fetch user info from Google
        google_user = await get_google_user_info(access_token)

        if not google_user:
            log.error("Failed to fetch Google user info")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user information from Google.",
            )

        google_id = google_user.get("id")
        email = google_user.get("email")
        name = google_user.get("name")
        picture = google_user.get("picture")

        log.info(f"Google OAuth for: {email}")

        # Check if user exists by Google ID
        user = await user_crud.get_user_by_google_id(google_id)

        if not user:
            # Check if user exists by email (might have registered with password)
            user = await user_crud.get_user_by_email(email)

            # If user still doesn't exist and intent is login, fail
            if not user and intent == "login":
                log.warning(f"Login failed for non-existent user: {email}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Account does not exist. Please sign up first.",
                )

            if user:
                # Link existing account with Google
                log.info(f"Linking existing account with Google: {email}")
                user = await user_crud.update_user_google_info(
                    user_id=str(user.id),
                    google_id=google_id,
                    profile_pic=picture,
                )
            else:
                # Create new user
                log.info(f"Creating new Google user: {email}")
                try:
                    user = await user_crud.create_google_user(
                        email=email,
                        full_name=name,
                        google_id=google_id,
                        profile_pic=picture,
                        role=role,
                    )
                except ValueError as e:
                    log.error(f"Failed to create Google user: {str(e)}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=str(e),
                    )

        # Check if user is active
        if not user.is_active:
            log.warning(f"Google login attempt for deactivated account: {email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )

        log.info(f"Google login successful for: {email}")

        # Create our app's JWT tokens
        tokens = create_tokens(user_id=str(user.id), role=user.role.value)

        return {
            "user": self._user_to_dict(user),
            "tokens": tokens,
            "message": "Google login successful",
        }

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """
        Convert User model to dictionary (excluding sensitive fields).

        Args:
            user: User model instance

        Returns:
            Dictionary representation of user (safe for API response)
        """
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "role": user.role.value,
            "profile_pic": user.profile_pic,
            "auth_provider": user.auth_provider,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }


# Create singleton instance for easy import
auth_controller = AuthController()
