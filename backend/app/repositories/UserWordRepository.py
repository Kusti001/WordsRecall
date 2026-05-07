from app.db.session import new_session
from app.models.word import Word
from app.models.user_word import UserWord
from app.repositories.UserRepository import UserRepository
from .base import BaseRepository
from sqlalchemy import delete, select, and_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta, timezone
import logging

logger = logging.getLogger(__name__)

class UserWordRepository(BaseRepository[UserWord]):
    model = UserWord

    @classmethod
    async def add_word_to_user(cls, user_id: int, word_id: int):
        """Add a word to the user's list of words. Returns dict with status and word details."""
        try:
            async with new_session() as session:
                # Check if the word is already added for the user
                query = select(UserWord).where(and_(UserWord.user_id == user_id, UserWord.word_id == word_id))
                existing = await session.execute(query)
                
                if existing.scalar_one_or_none():
                    # Word already exists - get word details
                    word = await session.get(Word, word_id)
                    return {
                        "status": "already_exists",
                        "word": word.word,
                        "translation": word.translation,
                        "meaning": word.meaning,
                        "example": word.example,
                        "level": word.level
                    }
                
                # Create new UserWord record with explicit next_review
                user_word = cls.model(
                    user_id=user_id, 
                    word_id=word_id,
                    next_review=datetime.now(timezone.utc)
                )
                session.add(user_word)
                await session.flush()
                
                # Get word details
                word = await session.get(Word, word_id)
                await session.commit()
                
                logger.info(f"Word {word.word} added to user {user_id}")
                return {
                    "status": "added",
                    "user_word_id": user_word.id,
                    "word": word.word,
                    "translation": word.translation,
                    "meaning": word.meaning,
                    "example": word.example,
                    "level": word.level
                }
            
        except SQLAlchemyError as e:
            logger.error(f"Database error adding word to user: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error adding word to user: {e}")
            raise


    @classmethod
    async def get_review_words(cls, user_id: int):
        """Get words that are due for review for a specific user"""
        try:
            async with new_session() as session:
                query = select(UserWord).options(selectinload(UserWord.word)).where(
                    and_(UserWord.user_id == user_id, UserWord.next_review <= datetime.now(timezone.utc))
                )
                result = await session.execute(query)
                return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting review words: {e}")
            raise

    @classmethod
    async def update_review(cls, user_word_id: int, result: str):
        """Update the review interval based on user's performance"""
        try:
            async with new_session() as session:
                user_word = await session.get(UserWord, user_word_id)
                
                if not user_word:
                    raise LookupError(f"UserWord with id {user_word_id} not found")
                
                # SM-2 like algorithm (more conservative than original)
                if result == "good":
                    user_word.repetitions += 1
                    user_word.interval *= 2  # More conservative growth
                elif result == "hard":
                    user_word.repetitions = max(0, user_word.repetitions - 1)
                    user_word.interval = max(1, int(user_word.interval / 2))
                elif result == "again":
                    user_word.repetitions = 0
                    user_word.interval = 1
                else:
                    raise ValueError(f"Invalid review result: {result}")

                # Calculate next review date based on interval (days)
                user_word.next_review = datetime.now(timezone.utc) + timedelta(days=user_word.interval)
                
                await session.merge(user_word)
                await session.commit()
                
                logger.info(f"Updated review for user_word {user_word_id}: result={result}, interval={user_word.interval}")
                return user_word
        except SQLAlchemyError as e:
            logger.error(f"Database error updating review: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating review: {e}")
            raise
        
    @classmethod
    async def get_user_dictionary(cls, user_id: int):
        """Get all words in the user's dictionary"""
        try:
            async with new_session() as session:
                query = select(UserWord).options(selectinload(UserWord.word)).where(UserWord.user_id == user_id)
                result = await session.execute(query)
                return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting dictionary: {e}")
            raise
    
    @classmethod
    async def delete_user_word(cls, user_word_id: int, user_id: int):
        """Delete a word from user's dictionary with validation"""
        try:
            async with new_session() as session:
                user_word = await session.get(UserWord, user_word_id)
                
                if not user_word:
                    raise LookupError(f"UserWord with id {user_word_id} not found")
                
                # Verify ownership
                if user_word.user_id != user_id:
                    logger.warning(f"Unauthorized delete attempt: user {user_id} tried to delete word {user_word_id}")
                    raise PermissionError("Unauthorized")
                
                await session.delete(user_word)
                await session.commit()
                logger.info(f"Deleted word {user_word_id} from user {user_id}")
                return user_word
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting word: {e}")
            raise
        
    @classmethod
    async def get_new_words(cls, user_id: int):
        """Get new words that the user has not added to their dictionary yet"""
        try:
            limit_info = await UserRepository.can_add_new_words(user_id)
        
            if not limit_info["can_add"]:
                return []
            
            limit = limit_info["remaining"]
            
            async with new_session() as session:
                # Subquery to get word_ids already added by the user
                subquery = select(UserWord.word_id).where(UserWord.user_id == user_id)
                
                # Get words that are not in the user's dictionary (random order)
                query = select(Word).where(~Word.id.in_(subquery)).order_by(func.random()).limit(limit)
                result = await session.execute(query)
                new_words: list[Word] = result.scalars().all()

                if not new_words:
                    return []

                # Automatically add these new words to the user's dictionary
                for word in new_words:
                    user_word = await cls.add_word_to_user(user_id=user_id, word_id=word.id)
                
                user_words_query = select(UserWord).options(selectinload(UserWord.word)).where(
                    UserWord.user_id == user_id,
                    UserWord.word_id.in_([w.id for w in new_words])
                )

                result = await session.execute(user_words_query)
                return result.scalars().all()

        except SQLAlchemyError as e:
            logger.error(f"Database error getting new words: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting new words: {e}")
            raise
        

    @classmethod
    async def delete_all_user_words(cls, user_id: int) -> int:
        """
        Удаляет все слова пользователя и возвращает количество удалённых записей
        """
        try:
            async with new_session() as session:

                # Удаляем все записи
                delete_query = delete(UserWord).where(UserWord.user_id == user_id)
                await session.execute(delete_query)
                
                await session.commit()
                return 1

        except SQLAlchemyError as e:
            logger.error(f"Database error deleting all words for user {user_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting all words: {e}")
            raise
        
    @classmethod
    async def get_user_stats(cls, user_id: int) -> dict:
        """Get user statistics like total words, words due for review, etc."""
        try:
            async with new_session() as session:
                total_query = select(func.count(UserWord.id)).where(UserWord.user_id == user_id)
                review_query = select(func.count(UserWord.id)).where(
                    and_(UserWord.user_id == user_id, UserWord.next_review <= datetime.now(timezone.utc))
                )
                
                total_result = await session.execute(total_query)
                review_result = await session.execute(review_query)
                
                total_words = total_result.scalar_one()
                review_words = review_result.scalar_one()
                
                return {
                    "total_words": total_words,
                    "review_words": review_words
                }
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user stats: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting user stats: {e}")
            raise