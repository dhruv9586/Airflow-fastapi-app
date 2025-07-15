from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database.connection import (
    connect_to_mongo,
    close_mongo_connection,
    get_database,
)
from app.routers.user import router as user_router
from app.routers.worker import router as worker_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to MongoDB when the application starts
    print("Starting application, connecting to MongoDB...")
    try:
        await connect_to_mongo()
        print("MongoDB connection successful")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        # You might want to exit the application here if DB connection is critical
        # import sys
        # sys.exit(1)

    yield  # The application runs here

    # Close MongoDB connection when the application shuts down
    print("Shutting down application...")
    await close_mongo_connection()
    print("MongoDB connection closed")


app = FastAPI(lifespan=lifespan)

# Include routers
app.include_router(user_router)
app.include_router(worker_router)


@app.get("/")
async def root():
    # Test database connection
    try:
        db = get_database()
        await db.command("ping")
        return {"message": "Hello World", "database_status": "connected"}
    except Exception as e:
        return {"message": "Hello World", "database_status": f"error: {str(e)}"}
