from fastapi import FastAPI
from contextlib import asynccontextmanager
from .routers.word import router as word_router
from .routers.users import router as users_router
from .core.database import create_tables, delete_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    await create_tables()
    yield
    print("Application shutdown")
    # Shutdown: Delete tables
    #await delete_tables()

app = FastAPI(lifespan=lifespan) # создаем экземпляр приложения FastAPI, который будет обрабатывать запросы и маршруты

app.include_router(word_router)
app.include_router(users_router)

# включаем маршруты из router в приложение FastAPI, чтобы они были доступны при обработке запросов
