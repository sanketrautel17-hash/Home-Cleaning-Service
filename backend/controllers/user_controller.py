"""
User Controller
===============
Business logic for user profile management operations.
Handles user profile CRUD operations separate from authentication.

Handles:
- Get user profile
- Update user profile
- Delete user account
- List users (admin)
"""

from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status

from cruds.user_crud import user_crud
from commons.logger import logger
from models.user_model import User

# Initialize logger
log = logger(__name__)


class UserController:
    """
    User profile management controller.

    This class contains all user profile-related business logic,
    separating it from route handlers for better maintainability.

    Usage:
        user_controller = UserController()
        result = await user_controller.get_profile(user)
    """

    # =========================================================================
    # GET PROFILE
    # =========================================================================

    async def get_profile(self, user: User) -> Dict[str, Any]:
        """
        Get current user's profile.

        Args:
            user: Current authenticated user

        Returns:
            Dictionary containing user profile data
        """
        log.info(f"Getting profile for user: {user.email}")

        return {"user": self._user_to_dict(user)}

    async def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        """
        Get a user's public profile by ID.

        Args:
            user_id: User's ID

        Returns:
            Dictionary containing public user data

        Raises:
            HTTPException 404: If user not found
        """
        log.info(f"Getting user by ID: {user_id}")

        user = await user_crud.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Return public profile only
        return {"user": self._user_to_public_dict(user)}

    # =========================================================================
    # UPDATE PROFILE
    # =========================================================================

    async def update_profile(
        self,
        user: User,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        profile_pic: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update current user's profile.

        Args:
            user: Current authenticated user
            full_name: Optional new full name
            phone: Optional new phone number
            profile_pic: Optional new profile picture URL

        Returns:
            Dictionary containing updated user profile

        Raises:
            HTTPException 500: If update fails
        """
        log.info(f"Updating profile for user: {user.email}")

        # Build update data
        update_data = {}
        if full_name is not None:
            update_data["full_name"] = full_name.strip()
        if phone is not None:
            update_data["phone"] = phone
        if profile_pic is not None:
            update_data["profile_pic"] = profile_pic

        if not update_data:
            # No updates provided, return current profile
            return {"user": self._user_to_dict(user), "message": "No changes made"}

        try:
            updated_user = await user_crud.update_user(
                user_id=str(user.id), **update_data
            )

            if not updated_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update profile",
                )

            log.info(f"Profile updated for user: {user.email}")

            return {
                "user": self._user_to_dict(updated_user),
                "message": "Profile updated successfully",
            }

        except Exception as e:
            log.error(f"Profile update error for {user.email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating profile",
            )

    # =========================================================================
    # DELETE ACCOUNT
    # =========================================================================

    async def delete_account(
        self,
        user: User,
        password: str,
    ) -> Dict[str, Any]:
        """
        Delete current user's account.

        Requires password confirmation for security.

        Args:
            user: Current authenticated user
            password: Password confirmation

        Returns:
            Dictionary with success message

        Raises:
            HTTPException 400: If password is incorrect
            HTTPException 500: If deletion fails
        """
        log.info(f"Account deletion requested for: {user.email}")

        # Verify password
        is_valid = await user_crud.verify_current_password(
            user_id=str(user.id), current_password=password
        )

        if not is_valid:
            log.warning(f"Wrong password for account deletion: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password"
            )

        # Delete account
        success = await user_crud.delete_user(str(user.id))

        if not success:
            log.error(f"Account deletion failed for: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete account",
            )

        log.info(f"Account deleted: {user.email}")

        return {"message": "Account deleted successfully", "success": True}

    async def deactivate_account(self, user: User) -> Dict[str, Any]:
        """
        Deactivate current user's account (soft delete).

        Args:
            user: Current authenticated user

        Returns:
            Dictionary with success message
        """
        log.info(f"Account deactivation for: {user.email}")

        success = await user_crud.deactivate_user(str(user.id))

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to deactivate account",
            )

        log.info(f"Account deactivated: {user.email}")

        return {"message": "Account deactivated successfully", "success": True}

    # =========================================================================
    # LIST USERS (For future admin use)
    # =========================================================================

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 20,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        List all users with pagination and filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum records to return (max 100)
            role: Optional role filter
            is_active: Optional active status filter

        Returns:
            Dictionary with users list and pagination info
        """
        log.info(f"Listing users: skip={skip}, limit={limit}")

        # Cap limit at 100
        limit = min(limit, 100)

        users = await user_crud.get_all_users(
            skip=skip, limit=limit, role=role, is_active=is_active
        )

        total = await user_crud.count_users(role=role, is_active=is_active)

        return {
            "users": [self._user_to_public_dict(u) for u in users],
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total,
                "has_more": skip + len(users) < total,
            },
        }

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """
        Convert User model to dictionary (all fields, for owner).

        Args:
            user: User model instance

        Returns:
            Full dictionary representation of user
        """
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "role": user.role.value,
            "profile_pic": user.profile_pic,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }

    def _user_to_public_dict(self, user: User) -> Dict[str, Any]:
        """
        Convert User model to dictionary (public fields only).

        Args:
            user: User model instance

        Returns:
            Public dictionary representation (hides sensitive data)
        """
        return {
            "id": str(user.id),
            "full_name": user.full_name,
            "role": user.role.value,
            "profile_pic": user.profile_pic,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }


# Create singleton instance for easy import
user_controller = UserController()
