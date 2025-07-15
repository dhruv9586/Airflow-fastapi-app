from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

# MONGODB CONNECTION
MONGODB_URL = "mongodb://localhost:27017/"
DB_NAME = "fastapi_db"

# Global variables for database connection
client: Optional[AsyncIOMotorClient] = None
db = None


async def connect_to_mongo():
    """Create database connection."""
    global client, db
    # Print for debugging
    print(f"Connecting to MongoDB at {MONGODB_URL}")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]
    # Test the connection
    await db.command("ping")
    print("MongoDB connection established successfully")
    return db


async def close_mongo_connection():
    """Close database connection."""
    global client
    if client is not None:
        print("Closing MongoDB connection")
        client.close()


def get_database():
    """Get database instance."""
    global db
    if db is None:
        # This is a safety check - db should be initialized via connect_to_mongo
        # But if it's not, we'll initialize it here
        print(
            "Warning: Database accessed before initialization, creating connection now"
        )
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client[DB_NAME]
    return db


def get_collection(collection_name: str):
    """Get specific collection from database."""
    database = get_database()
    return database[collection_name]
