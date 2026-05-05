
from sqlalchemy import select
from app.db.session import new_session
from typing import TypeVar, Generic, Type

T = TypeVar('T')  # Generic type for models

class BaseRepository(Generic[T]):
    """Base repository providing common database operations for all models."""
    model: Type[T]  # Subclasses set their own model

    @classmethod
    async def get_by_id(cls, id: int):
        """Get a record by ID"""
        async with new_session() as session:
            return await session.get(cls.model, id)

    @classmethod
    async def get_all(cls):
        """Get all records"""
        async with new_session() as session:
            result = await session.execute(select(cls.model))
            return result.scalars().all()
        
    @classmethod
    async def create(cls, **kwargs):
        """Create a new record"""
        async with new_session() as session:
            obj = cls.model(**kwargs)
            session.add(obj)
            await session.flush()
            await session.commit()
            return obj

    @classmethod
    async def delete(cls, id: int):
        """Delete a record"""
        async with new_session() as session:
            obj = await session.get(cls.model, id)
            if obj:
                await session.delete(obj)
                await session.commit()
            return obj