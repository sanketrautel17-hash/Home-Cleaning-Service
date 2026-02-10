"""
Create Database Indexes
=======================
Script to create necessary MongoDB indexes, especially geospatial ones
that are not automatically handled by ODMantic.

Usage:
    python -m scripts.create_indexes
"""

import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import connect_to_mongo, db_instance, close_mongo_connection
from models.cleaner_profile_model import CleanerProfile
from commons.logger import logger

log = logger(__name__)


async def create_indexes():
    """Create all necessary indexes."""
    log.info("Connecting to database...")
    await connect_to_mongo()

    db = db_instance.client[os.getenv("DATABASE_NAME", "authentication")]

    # =========================================================================
    # Cleaner Profile Indexes
    # =========================================================================

    collection = db["cleaner_profiles"]

    # 1. Geospatial Index for location search
    # This is critical for $geoNear queries
    log.info("Creating 2dsphere index on cleaner_profiles.location...")
    await collection.create_index([("location", "2dsphere")])

    # 2. Compound index for common search filters
    # city + specializations is a very common query
    log.info("Creating compound index on city + specializations...")
    await collection.create_index([("city", 1), ("specializations", 1)])

    # 3. Index for availability
    log.info("Creating index on is_available...")
    await collection.create_index("is_available")

    # =========================================================================
    # Service Package Indexes
    # =========================================================================

    services_collection = db["services"]

    # 1. Index for category search
    log.info("Creating index on services.category...")
    await services_collection.create_index("category")

    # 2. Index for cleaner_id (to finding services by cleaner)
    log.info("Creating index on services.cleaner_id...")
    await services_collection.create_index("cleaner_id")

    # 3. Index for price sorting
    log.info("Creating index on services.price...")
    await services_collection.create_index("price")

    log.info("All indexes created successfully!")
    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(create_indexes())
