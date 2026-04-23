from app.core.database import UserWord, Word, new_session
from .base import BaseRepository
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta

class UserWordRepository(BaseRepository[UserWord]):
    model = UserWord

    @classmethod
    async def add_word_to_user(cls, user_id: int, word_id: int):
        """Add a word to the user's list of words"""
        async with new_session() as session:
            # Check if the word is already added for the user
            query = select(UserWord).where(and_(UserWord.user_id == user_id, UserWord.word_id == word_id))
            existing = await session.execute(query)
            
            if existing.scalar_one_or_none():
                return {"message": "word already added", "word": (await session.get(Word, word_id)).word}
            
            await cls.create(user_id=user_id, word_id=word_id)
            return {"message": "word_added", "word": (await session.get(Word, word_id)).word}


    @classmethod
    async def get_review_words(cls, user_id: int):
        """Get words that are due for review for a specific user"""
        async with new_session() as session:
            query = select(UserWord).options(selectinload(UserWord.word)).where(and_(UserWord.user_id == user_id, UserWord.next_review <= datetime.now()))
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def update_review(cls, user_word_id: int, result: str):
        """Update the review interval"""
        async with new_session() as session:
            user_word = await session.get(UserWord, user_word_id)
            
            if result == "good":
                user_word.repetitions += 1
                user_word.interval *= 7
            elif result == "hard":
                user_word.repetitions += 1
                user_word.interval = 3
            elif result == "again":
                user_word.repetitions += 1
                user_word.interval = 1

            # Calculate the next review date based on the updated interval(days)
            user_word.next_review = datetime.now() + timedelta(days=user_word.interval)
            
            await session.merge(user_word)
            await session.commit()
            return user_word