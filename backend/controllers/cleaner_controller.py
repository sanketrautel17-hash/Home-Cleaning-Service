"""
Cleaner Controller
==================
Business logic for cleaner profile management operations.

Handles:
- Create cleaner profile (role check + duplicate check)
- Get cleaner profile (own / public)
- Update cleaner profile
- Search cleaners (by city, rating, specialization)
- Find nearby cleaners (location-based)
"""

from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status

from cruds.cleaner_crud import cleaner_crud
from cruds.user_crud import user_crud
from commons.logger import logger
from models.user_model import User
from models.cleaner_profile_model import CleanerProfile

# Initialize logger
log = logger(__name__)


class CleanerController:
    """
    Cleaner profile management controller.

    This class contains all cleaner profile-related business logic,
    including role checks, profile creation, updates, and search.

    Usage:
        cleaner_controller = CleanerController()
        result = await cleaner_controller.create_profile(user, profile_data)
    """

    # =========================================================================
    # CREATE PROFILE
    # =========================================================================

    async def create_profile(
        self,
        user: User,
        bio: Optional[str] = None,
        experience_years: int = 0,
        specializations: Optional[List[str]] = None,
        address: Optional[str] = None,
        city: str = "",
        state: Optional[str] = None,
        pincode: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        service_radius_km: float = 10.0,
    ) -> Dict[str, Any]:
        """
        Create a cleaner profile for the current user.

        Business rules:
        - Only users with role='cleaner' can create a profile
        - Each cleaner can have only ONE profile
        - City is required for search functionality

        Args:
            user: Current authenticated user (must be a cleaner)
            bio: Professional bio text
            experience_years: Years of experience
            specializations: List of service categories
            address: Full street address
            city: City name (required)
            state: State name
            pincode: Postal code
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            service_radius_km: Travel distance in km

        Returns:
            Dictionary with created profile data

        Raises:
            HTTPException 403: If user is not a cleaner
            HTTPException 409: If profile already exists
        """
        log.info(f"Creating cleaner profile for user: {user.email}")

        # Role check - only cleaners can create profiles
        if user.role.value != "cleaner":
            log.warning(f"Non-cleaner user tried to create profile: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only users with 'cleaner' role can create a cleaner profile",
            )

        # Check for existing profile
        existing = await cleaner_crud.get_profile_by_user_id(str(user.id))
        if existing:
            log.warning(f"Duplicate profile creation attempt: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cleaner profile already exists. Use update instead.",
            )

        # Build profile data
        profile_data = {
            "user_id": str(user.id),
            "bio": bio,
            "experience_years": experience_years,
            "specializations": specializations or ["regular"],
            "address": address,
            "city": city,
            "state": state,
            "pincode": pincode,
            "latitude": latitude,
            "longitude": longitude,
            "service_radius_km": service_radius_km,
        }

        try:
            log.info(
                f"Calling cleaner_crud.create_profile with type {type(profile_data)}"
            )
            log.info(f"Data: {profile_data}")
            profile = await cleaner_crud.create_profile(profile_data)
            log.info(f"Cleaner profile created for: {user.email} in {city}")

            return {
                "profile": self._profile_to_dict(profile),
                "message": "Cleaner profile created successfully",
                "success": True,
            }

        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except Exception as e:
            import traceback

            log.error(f"Profile creation error for {user.email}: {str(e)}")
            log.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating the profile",
            )

    # =========================================================================
    # GET PROFILE
    # =========================================================================

    async def get_my_profile(self, user: User) -> Dict[str, Any]:
        """
        Get the current cleaner's own profile (full details).

        Args:
            user: Current authenticated user

        Returns:
            Dictionary with full profile data (includes address, pincode)

        Raises:
            HTTPException 403: If user is not a cleaner
            HTTPException 404: If profile not found
        """
        log.info(f"Getting cleaner profile for: {user.email}")

        if user.role.value != "cleaner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only cleaners have cleaner profiles",
            )

        profile = await cleaner_crud.get_profile_by_user_id(str(user.id))
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cleaner profile not found. Create one first.",
            )

        return {"profile": self._profile_to_dict(profile)}

    async def get_public_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get a cleaner's public profile (for customers browsing).

        Excludes private info like full address and pincode.
        Includes user's name and profile picture.

        Args:
            user_id: Cleaner's user ID

        Returns:
            Dictionary with public profile data

        Raises:
            HTTPException 404: If cleaner profile not found
        """
        log.info(f"Getting public cleaner profile for user: {user_id}")

        profile = await cleaner_crud.get_profile_by_user_id(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cleaner profile not found",
            )

        # Get user info for name and profile pic
        user = await user_crud.get_user_by_id(user_id)

        return {"profile": self._profile_to_public_dict(profile, user)}

    # =========================================================================
    # UPDATE PROFILE
    # =========================================================================

    async def update_profile(
        self,
        user: User,
        update_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update the current cleaner's profile.

        Args:
            user: Current authenticated user
            update_data: Dictionary of fields to update

        Returns:
            Dictionary with updated profile data

        Raises:
            HTTPException 403: If user is not a cleaner
            HTTPException 404: If profile not found
        """
        log.info(f"Updating cleaner profile for: {user.email}")

        if user.role.value != "cleaner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only cleaners can update cleaner profiles",
            )

        # Filter out None values
        clean_data = {k: v for k, v in update_data.items() if v is not None}

        if not clean_data:
            profile = await cleaner_crud.get_profile_by_user_id(str(user.id))
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cleaner profile not found",
                )
            return {
                "profile": self._profile_to_dict(profile),
                "message": "No changes made",
            }

        try:
            updated_profile = await cleaner_crud.update_profile(
                user_id=str(user.id), update_data=clean_data
            )

            if not updated_profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cleaner profile not found. Create one first.",
                )

            log.info(f"Cleaner profile updated for: {user.email}")

            return {
                "profile": self._profile_to_dict(updated_profile),
                "message": "Profile updated successfully",
                "success": True,
            }

        except Exception as e:
            log.error(f"Profile update error for {user.email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating the profile",
            )

    # =========================================================================
    # SEARCH CLEANERS
    # =========================================================================

    async def search_cleaners(
        self,
        city: Optional[str] = None,
        specialization: Optional[str] = None,
        min_rating: Optional[float] = None,
        is_available: Optional[bool] = None,
        verified: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "rating",
    ) -> Dict[str, Any]:
        """
        Search for cleaners with filters and pagination.

        Args:
            city: Filter by city
            specialization: Filter by service category
            min_rating: Minimum average rating
            is_available: Filter by availability
            verified: Filter by verification status
            skip: Pagination offset
            limit: Max results (capped at 50)
            sort_by: Sort field

        Returns:
            Dictionary with cleaner list and pagination
        """
        log.info(f"Searching cleaners: city={city}, spec={specialization}")

        # Cap limit
        limit = min(limit, 50)

        profiles = await cleaner_crud.search_cleaners(
            city=city,
            specialization=specialization,
            min_rating=min_rating,
            is_available=is_available,
            verified=verified,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
        )

        total = await cleaner_crud.count_cleaners(
            city=city,
            specialization=specialization,
            min_rating=min_rating,
            is_available=is_available,
            verified=verified,
        )

        # Enrich profiles with user info (name, profile pic)
        enriched = []
        for profile in profiles:
            user = await user_crud.get_user_by_id(profile.user_id)
            enriched.append(self._profile_to_public_dict(profile, user))

        return {
            "cleaners": enriched,
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total,
                "has_more": skip + len(profiles) < total,
            },
        }

    async def find_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Find cleaners near a given location.

        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius_km: Search radius in km (max 50)
            limit: Max results (max 50)

        Returns:
            Dictionary with nearby cleaners list
        """
        log.info(
            f"Finding nearby cleaners: lat={latitude}, lng={longitude}, "
            f"radius={radius_km}km"
        )

        # Cap values
        radius_km = min(radius_km, 50.0)
        limit = min(limit, 50)

        profiles = await cleaner_crud.find_nearby_cleaners(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            limit=limit,
        )

        # Enrich with user info
        enriched = []
        for profile in profiles:
            user = await user_crud.get_user_by_id(profile.user_id)
            enriched.append(self._profile_to_public_dict(profile, user))

        return {
            "cleaners": enriched,
            "search": {
                "latitude": latitude,
                "longitude": longitude,
                "radius_km": radius_km,
            },
            "total": len(enriched),
        }

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _profile_to_dict(self, profile: CleanerProfile) -> Dict[str, Any]:
        """
        Convert CleanerProfile to full dictionary (for owner).

        Includes all fields including address and pincode.
        """
        location_data = profile.location

        return {
            "id": str(profile.id),
            "user_id": profile.user_id,
            "bio": profile.bio,
            "experience_years": profile.experience_years,
            "specializations": list(profile.specializations),
            "address": profile.address,
            "city": profile.city,
            "state": profile.state,
            "pincode": profile.pincode,
            "location": location_data,
            "service_radius_km": profile.service_radius_km,
            "is_available": profile.is_available,
            "verified": profile.verified,
            "avg_rating": profile.avg_rating,
            "total_reviews": profile.total_reviews,
            "completed_jobs": profile.completed_jobs,
            "created_at": (
                profile.created_at.isoformat() if profile.created_at else None
            ),
            "updated_at": (
                profile.updated_at.isoformat() if profile.updated_at else None
            ),
        }

    def _profile_to_public_dict(
        self, profile: CleanerProfile, user: Optional[User] = None
    ) -> Dict[str, Any]:
        """
        Convert CleanerProfile to public dictionary (for customers).

        Hides private data (address, pincode).
        Adds user's name and profile pic if available.
        """
        return {
            "id": str(profile.id),
            "user_id": profile.user_id,
            "full_name": user.full_name if user else None,
            "profile_pic": user.profile_pic if user else None,
            "bio": profile.bio,
            "experience_years": profile.experience_years,
            "specializations": list(profile.specializations),
            "city": profile.city,
            "state": profile.state,
            "service_radius_km": profile.service_radius_km,
            "is_available": profile.is_available,
            "verified": profile.verified,
            "avg_rating": profile.avg_rating,
            "total_reviews": profile.total_reviews,
            "completed_jobs": profile.completed_jobs,
            "created_at": (
                profile.created_at.isoformat() if profile.created_at else None
            ),
        }


# Create singleton instance for easy import
cleaner_controller = CleanerController()
