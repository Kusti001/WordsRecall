from fastapi import FastAPI
from contextlib import asynccontextmanager
from .core.database import create_tables, delete_tables
from .api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    await create_tables()
    yield
    print("Application shutdown")
    # Shutdown: Delete tables
    #await delete_tables()

# Create FastAPI application with lifespan context manager for startup and shutdown events
app = FastAPI(lifespan=lifespan)

# Include API routers for words and users
app.include_router(api_router)

