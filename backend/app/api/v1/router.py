from fastapi import APIRouter
from .endpoints import User, Word

api_router = APIRouter()
api_router.include_router(User.router)
api_router.include_router(Word.router)
