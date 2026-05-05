import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .db.init_db import create_tables, delete_tables
from .api.v1.router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    logger.info("Starting up: Creating database tables")
    await create_tables()
    logger.info("Application started successfully")
    yield
    logger.info("Shutting down application")
    # Shutdown: Delete tables (commented out to preserve data)
    #await delete_tables()

# Create FastAPI application with lifespan context manager for startup and shutdown events
app = FastAPI(
    title="Words API",
    description="API for learning English words with spaced repetition",
    version="1.0.0",
    lifespan=lifespan
)

# Include API routers for words and users
app.include_router(api_router)
