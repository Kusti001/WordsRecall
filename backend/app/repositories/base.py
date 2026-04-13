
from sqlalchemy import select

from app.core.database import new_session
from typing import TypeVar, Generic, Type

T = TypeVar('T')  # Generic тип для модели

class BaseRepository(Generic[T]):
    """Базовый репозиторий со стандартными операциями"""
    model: Type[T]  # Подклассы устанавливают свою модель

    @classmethod
    async def get_by_id(cls, id: int):
        """Получить запись по ID"""
        async with new_session() as session:
            return await session.get(cls.model, id)

    @classmethod
    async def get_all(cls):
        """Получить все записи"""
        async with new_session() as session:
            result = await session.execute(select(cls.model))
            return result.scalars().all()
        
    @classmethod
    async def create(cls, **kwargs):
        """Создать новую запись"""
        async with new_session() as session:
            obj = cls.model(**kwargs)
            session.add(obj)
            await session.flush()
            await session.commit()
            return obj

    @classmethod
    async def delete(cls, id: int):
        """Удалить запись"""
        async with new_session() as session:
            obj = await session.get(cls.model, id)
            if obj:
                await session.delete(obj)
                await session.commit()
            return obj