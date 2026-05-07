from datetime import date
from app.db.session import new_session
from app.models.user import User
from .base import BaseRepository
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class UserRepository(BaseRepository[User]):
    model = User

    @classmethod
    async def get_by_telegram_id(cls, telegram_id: str):
        """Get a user by Telegram ID"""
        try:
            async with new_session() as session:
                query = select(User).where(User.telegram_id == telegram_id)
                result = await session.execute(query)
                return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user by telegram_id: {e}")
            raise

    @classmethod
    async def create_user(cls, telegram_id: str):
        """Create a new user"""
        try:
            return await cls.create(telegram_id=telegram_id)

        except SQLAlchemyError as e:
            logger.error(f"Database error creating user: {e}")
            raise
        
    @classmethod
    async def can_add_new_words(cls, user_id: int) -> dict:
        """
        Проверяет, можно ли добавить новые слова сегодня
        """
        try:
            async with new_session() as session:
                user = await session.get(User, user_id)
                if not user:
                    return {"can_add": False, "remaining": 0, "error": "User not found"}

                today = date.today()

                # Если сегодня ещё не добавляли — сбрасываем счётчик
                if user.last_new_words_date != today:
                    user.new_words_added_today = 0
                    user.last_new_words_date = today
                    await session.commit()

#NEED TO REWRITE!!!!!!!!!
            
                can_add = user.new_words_limit - user.new_words_added_today

                user.new_words_added_today = user.new_words_limit
                await session.commit()

                if can_add > 0:
                    return {"can_add": True, "remaining": can_add}
                else:
                    return {"can_add": False, "remaining": 0}

        except Exception as e:
            logger.error(f"Error checking new words limit: {e}")
            raise