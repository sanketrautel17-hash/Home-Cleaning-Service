import os
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from dotenv import load_dotenv
from core import logger

load_dotenv()

logging = logger(__name__)


class Database:
    # Step 1: Hold MongoDB client
    client: AsyncIOMotorClient | None = None

    # Step 2: Hold ODMantic engine
    engine: AIOEngine | None = None


# Step 3: Create a single shared database instance
db_instance = Database()


async def connect_to_mongo():
    # Step 4: Create MongoDB client (lazy connection)
    try:
        db_instance.client = AsyncIOMotorClient(
            os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        )

        # Step 5: Create ODMantic engine using the client
        db_instance.engine = AIOEngine(
            client=db_instance.client,
            database=os.getenv("DATABASE_NAME", "authentication"),
        )

        # Step 6: Force a real connection check
        await db_instance.client[os.getenv("DATABASE_NAME", "authentication")].command(
            "ping"
        )
        logging.info("Connected to MongoDB")
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")


async def close_mongo_connection():
    # Step 7: Close MongoDB client during shutdown
    if db_instance.client:
        db_instance.client.close()
        logging.info("Closed MongoDB connection")


def get_engine() -> AIOEngine:
    # Step 8: Provide ODMantic engine for CRUD operations
    return db_instance.engine
