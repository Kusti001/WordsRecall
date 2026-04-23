from app.core.database import Review
from .base import BaseRepository

class ReviewRepository(BaseRepository[Review]):
    model = Review

    @classmethod
    async def log_review(cls, user_word_id: int, result: str):
        """Log a review attempt"""
        return await cls.create(user_word_id=user_word_id, result=result)

    @classmethod
    async def get_user_stats(cls, user_id: int):
        """Get user review statistics, e.g. number of correct reviews per day"""
        pass