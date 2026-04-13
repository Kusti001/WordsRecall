from app.core.database import UserWord, User, Word, new_session
from .base import BaseRepository
from sqlalchemy import select, and_
from datetime import datetime, timedelta
#from ..services.spaced_repetition import calculate_next_review

class UserWordRepository(BaseRepository[UserWord]):
    model = UserWord

    @classmethod
    async def add_word_to_user(cls, user_id: int, word_id: int):
        """Добавить слово в список пользователя"""
        async with new_session() as session:
            # Проверяем, не добавлено ли уже
            query = select(UserWord).where(
                and_(
                    UserWord.user_id == user_id,
                    UserWord.word_id == word_id
                )
            )
            existing = await session.execute(query)
            
            if existing.scalar_one_or_none():
                return {"error": "Word already added"}
            
            user_word = UserWord(user_id=user_id, word_id=word_id)
            session.add(user_word)
            await session.commit()
            return user_word

    @classmethod
    async def get_review_words(cls, user_id: int):
        """Получить слова, готовые к повторению"""
        async with new_session() as session:
            query = select(UserWord).where(
                and_(
                    UserWord.user_id == user_id,
                    UserWord.next_review <= datetime.now()
                )
            )
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def update_review(cls, user_word_id: int, is_correct: bool):
        """Обновить интервал повторения"""
        async with new_session() as session:
            user_word = await session.get(UserWord, user_word_id)
            
            if is_correct:
                user_word.repetitions += 1
                user_word.interval *= 2
            else:
                user_word.repetitions = 0
                user_word.interval = 1
            
            # Вычисляем на Python следующую дату повторения
            user_word.next_review = datetime.now() + timedelta(days=user_word.interval)
            
            await session.merge(user_word)
            await session.commit()
            return user_word