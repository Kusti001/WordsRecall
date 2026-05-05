from fastapi import APIRouter
from .endpoints import user, word, user_word, review

api_router = APIRouter()
api_router.include_router(user.router)
api_router.include_router(word.router)
api_router.include_router(user_word.router)
api_router.include_router(review.router)
