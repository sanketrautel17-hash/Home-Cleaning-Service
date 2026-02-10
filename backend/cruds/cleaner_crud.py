"""
Cleaner CRUD Operations
=======================
Database operations for CleanerProfile model using ODMantic.
Handles all cleaner profile-related database queries and mutations.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from odmantic import AIOEngine

from models.cleaner_profile_model import CleanerProfile, ServiceCategory, Location
from database.database import get_engine
import logging


class CleanerCRUD:
    """
    CRUD operations for CleanerProfile model.

    All methods are async and use ODMantic engine for MongoDB operations.

    Usage:
        cleaner_crud = CleanerCRUD()
        profile = await cleaner_crud.create_profile(user_id="...", city="Mumbai", ...)
    """

    def __init__(self, engine: Optional[AIOEngine] = None):
        """
        Initialize CleanerCRUD with optional custom engine.

        Args:
            engine: Optional ODMantic engine. If not provided, uses default.
        """
        self._engine = engine

    @property
    def engine(self) -> AIOEngine:
        """Get the ODMantic engine."""
        return self._engine or get_engine()

    # =========================================================================
    # CREATE Operations
    # =========================================================================

    async def create_profile(self, profile_data: Dict[str, Any]) -> CleanerProfile:
        """
        Create a new cleaner profile.

        Args:
            profile_data: Dictionary containing profile fields:
                - user_id (required): Reference to the User
                - city (required): City name for search
                - bio, experience_years, specializations, address,
                  state, pincode, latitude, longitude, service_radius_km

        Returns:
            Created CleanerProfile object

        Raises:
            ValueError: If cleaner already has a profile
        """
        try:
            user_id = profile_data["user_id"]
        except Exception as e:
            raise

        # Check if profile already exists
        existing = await self.get_profile_by_user_id(user_id)
        if existing:
            raise ValueError(f"Cleaner profile already exists for user {user_id}")

        # Build location if coordinates are provided
        location = None
        lat = profile_data.get("latitude")
        lng = profile_data.get("longitude")
        if lat is not None and lng is not None:
            location = Location(type="Point", coordinates=[lng, lat])

        # Convert specialization strings to enums
        specializations = []
        spec_list = profile_data.get("specializations", ["regular"])
        for spec in spec_list:
            try:
                specializations.append(ServiceCategory(spec.lower()).value)
            except ValueError:
                # Default to regular if invalid
                specializations.append(ServiceCategory.REGULAR.value)

        # Build the document dict directly for raw insert
        # (Workaround for odmantic 1.0.3 bug #370/#485 with List + Optional EmbeddedModel)
        now = datetime.utcnow()
        profile_doc = {
            "user_id": user_id,
            "bio": profile_data.get("bio"),
            "experience_years": profile_data.get("experience_years", 0),
            "specializations": specializations,
            "address": profile_data.get("address"),
            "city": profile_data.get("city", "").strip(),
            "state": profile_data.get("state"),
            "pincode": profile_data.get("pincode"),
            "location": (
                {"type": location.type, "coordinates": location.coordinates}
                if location
                else None
            ),
            "service_radius_km": profile_data.get("service_radius_km", 10.0),
            "is_available": True,
            "verified": False,
            "avg_rating": 0.0,
            "total_reviews": 0,
            "completed_jobs": 0,
            "created_at": now,
            "updated_at": now,
        }

        # Use raw MongoDB insert to avoid odmantic serialization bug
        collection = self.engine.get_collection(CleanerProfile)
        result = await collection.insert_one(profile_doc)

        # Fetch back as ODMantic model for consistency
        profile = await self.engine.find_one(
            CleanerProfile, CleanerProfile.id == result.inserted_id
        )
        return profile

    # =========================================================================
    # READ Operations
    # =========================================================================

    async def get_profile_by_id(self, profile_id: str) -> Optional[CleanerProfile]:
        """Get a cleaner profile by its ID."""
        try:
            return await self.engine.find_one(
                CleanerProfile, CleanerProfile.id == ObjectId(profile_id)
            )
        except Exception:
            return None

    async def get_profile_by_user_id(self, user_id: str) -> Optional[CleanerProfile]:
        """Get a cleaner profile by the user's ID."""
        return await self.engine.find_one(
            CleanerProfile, CleanerProfile.user_id == user_id
        )

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
    ) -> List[CleanerProfile]:
        """Search cleaner profiles with filters."""
        filters = []

        if city:
            filters.append(CleanerProfile.city == city.strip())

        if specialization:
            category = ServiceCategory(specialization.lower())
            filters.append(CleanerProfile.specializations == category)

        if min_rating is not None:
            filters.append(CleanerProfile.avg_rating >= min_rating)

        if is_available is not None:
            filters.append(CleanerProfile.is_available == is_available)

        if verified is not None:
            filters.append(CleanerProfile.verified == verified)

        # Execute query
        if filters:
            profiles = await self.engine.find(
                CleanerProfile, *filters, skip=skip, limit=limit
            )
        else:
            profiles = await self.engine.find(CleanerProfile, skip=skip, limit=limit)

        # Sort results
        result = list(profiles)
        if sort_by == "rating":
            result.sort(key=lambda p: p.avg_rating, reverse=True)
        elif sort_by == "experience":
            result.sort(key=lambda p: p.experience_years, reverse=True)
        elif sort_by == "reviews":
            result.sort(key=lambda p: p.total_reviews, reverse=True)
        elif sort_by == "jobs":
            result.sort(key=lambda p: p.completed_jobs, reverse=True)

        return result

    async def count_cleaners(
        self,
        city: Optional[str] = None,
        specialization: Optional[str] = None,
        min_rating: Optional[float] = None,
        is_available: Optional[bool] = None,
        verified: Optional[bool] = None,
    ) -> int:
        """Count for pagination."""
        filters = []

        if city:
            filters.append(CleanerProfile.city == city.strip())

        if specialization:
            category = ServiceCategory(specialization.lower())
            filters.append(CleanerProfile.specializations == category)

        if min_rating is not None:
            filters.append(CleanerProfile.avg_rating >= min_rating)

        if is_available is not None:
            filters.append(CleanerProfile.is_available == is_available)

        if verified is not None:
            filters.append(CleanerProfile.verified == verified)

        if filters:
            return await self.engine.count(CleanerProfile, *filters)
        else:
            return await self.engine.count(CleanerProfile)

    async def find_nearby_cleaners(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0,
        limit: int = 20,
    ) -> List[CleanerProfile]:
        """Find cleaners near a given location."""
        # MongoDB $geoNear requires distance in meters
        radius_meters = radius_km * 1000

        collection = self.engine.get_collection(CleanerProfile)
        pipeline = [
            {
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": [longitude, latitude],
                    },
                    "distanceField": "distance_meters",
                    "maxDistance": radius_meters,
                    "spherical": True,
                    "query": {"is_available": True},
                }
            },
            {"$limit": limit},
        ]

        results = []
        async for doc in collection.aggregate(pipeline):
            try:
                profile = await self.get_profile_by_id(str(doc["_id"]))
                if profile:
                    results.append(profile)
            except Exception:
                continue

        return results

    # =========================================================================
    # UPDATE Operations
    # =========================================================================

    async def update_profile(
        self, user_id: str, update_data: Dict[str, Any]
    ) -> Optional[CleanerProfile]:
        """Update cleaner profile fields."""
        profile = await self.get_profile_by_user_id(user_id)
        if not profile:
            return None

        # Build $set dict for raw MongoDB update
        set_fields = {}

        # Direct fields that can be updated
        allowed_fields = {
            "bio",
            "experience_years",
            "address",
            "city",
            "state",
            "pincode",
            "service_radius_km",
            "is_available",
        }

        for field, value in update_data.items():
            if field in allowed_fields and value is not None:
                set_fields[field] = value

        # Handle specializations separately (need enum conversion)
        if (
            "specializations" in update_data
            and update_data["specializations"] is not None
        ):
            specs = []
            for spec in update_data["specializations"]:
                try:
                    specs.append(ServiceCategory(spec.lower()).value)
                except ValueError:
                    pass
            set_fields["specializations"] = specs

        # Handle location update
        lat = update_data.get("latitude")
        lng = update_data.get("longitude")
        if lat is not None and lng is not None:
            set_fields["location"] = {
                "type": "Point",
                "coordinates": [lng, lat],
            }

        # Update timestamp
        set_fields["updated_at"] = datetime.utcnow()

        # Use raw MongoDB update to avoid odmantic serialization bug
        collection = self.engine.get_collection(CleanerProfile)
        await collection.update_one({"_id": profile.id}, {"$set": set_fields})

        # Fetch back as ODMantic model
        return await self.get_profile_by_user_id(user_id)

    async def update_availability(
        self, user_id: str, is_available: bool
    ) -> Optional[CleanerProfile]:
        """Toggle cleaner's availability status."""
        profile = await self.get_profile_by_user_id(user_id)
        if not profile:
            return None

        collection = self.engine.get_collection(CleanerProfile)
        await collection.update_one(
            {"_id": profile.id},
            {"$set": {"is_available": is_available, "updated_at": datetime.utcnow()}},
        )
        return await self.get_profile_by_user_id(user_id)

    async def update_rating(
        self, user_id: str, new_avg: float, total_reviews: int
    ) -> Optional[CleanerProfile]:
        """Update cleaner's rating stats."""
        profile = await self.get_profile_by_user_id(user_id)
        if not profile:
            return None

        collection = self.engine.get_collection(CleanerProfile)
        await collection.update_one(
            {"_id": profile.id},
            {
                "$set": {
                    "avg_rating": round(new_avg, 2),
                    "total_reviews": total_reviews,
                    "updated_at": datetime.utcnow(),
                }
            },
        )
        return await self.get_profile_by_user_id(user_id)

    async def increment_completed_jobs(self, user_id: str) -> Optional[CleanerProfile]:
        """Increment completed jobs count."""
        profile = await self.get_profile_by_user_id(user_id)
        if not profile:
            return None

        collection = self.engine.get_collection(CleanerProfile)
        await collection.update_one(
            {"_id": profile.id},
            {"$inc": {"completed_jobs": 1}, "$set": {"updated_at": datetime.utcnow()}},
        )
        return await self.get_profile_by_user_id(user_id)

    # =========================================================================
    # DELETE Operations
    # =========================================================================

    async def delete_profile(self, user_id: str) -> bool:
        """Permanently delete a cleaner profile."""
        profile = await self.get_profile_by_user_id(user_id)
        if not profile:
            return False

        await self.engine.delete(profile)
        return True


# Create a singleton instance for easy import
cleaner_crud = CleanerCRUD()
