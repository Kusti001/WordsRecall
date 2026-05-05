
from app.models.review import Review
from .base import BaseRepository
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class ReviewRepository(BaseRepository[Review]):
    model = Review

    @classmethod
    async def log_review(cls, user_word_id: int, result: str):
        """Log a review attempt"""
        try:
            return await cls.create(user_word_id=user_word_id, result=result)
        except SQLAlchemyError as e:
            logger.error(f"Database error logging review: {e}")
            raise

    @classmethod
    async def get_user_stats(cls, user_id: int):
        """Get user review statistics"""
        # TODO: Implement statistics calculation
        pass