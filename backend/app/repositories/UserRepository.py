from app.core.database import User, new_session
from .base import BaseRepository
from sqlalchemy import select

class UserRepository(BaseRepository[User]):
    model = User

    @classmethod
    async def get_by_telegram_id(cls, telegram_id: str):
        """Get a user by Telegram ID"""
        async with new_session() as session:
            query = select(User).where(User.telegram_id == telegram_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def create_user(cls, telegram_id: str):
        """Create a new user"""
        return await cls.create(telegram_id=telegram_id)