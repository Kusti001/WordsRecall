from app.core.database import Review, new_session
from .base import BaseRepository

class ReviewRepository(BaseRepository[Review]):
    model = Review

    @classmethod
    async def log_review(cls, user_word_id: int, result: str):
        """Зафиксировать попытку"""
        return await cls.create(user_word_id=user_word_id, result=result)

    # Опционально: статистика пользователя
    @classmethod
    async def get_user_stats(cls, user_id: int):
        """Получить статистику пользователя по ревью"""
        # SELECT COUNT(*) WHERE result='correct' GROUP BY DATE
        pass