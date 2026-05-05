from app.db.session import new_session
from app.models.word import Word
from .base import BaseRepository
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from ..utils.word_enrichment import enrich_word_text
import logging

logger = logging.getLogger(__name__)

class WordRepository(BaseRepository[Word]):
    model = Word

    @classmethod
    async def get_by_word(cls, word_text: str):
        """get word by english text"""
        try:
            async with new_session() as session:
                query = select(Word).where(Word.word == word_text)
                result = await session.execute(query)
                return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting word by text: {e}")
            raise

    @classmethod
    async def get_all_words(cls):
        """get all words"""
        try:
            return await cls.get_all()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting all words: {e}")
            raise

    @classmethod
    async def get_or_create(cls, word_text: str):
        """get word, if it doesn't exist — create it using the local Ollama model."""
        try:
            word = await cls.get_by_word(word_text)
            
            if not word:
                try:
                    enriched = await enrich_word_text(word_text)
                    word = await cls.create(
                        word=enriched.word,
                        level=enriched.level,
                        meaning=enriched.meaning,
                        example=enriched.example,
                        translation=enriched.translation,
                    )
                    logger.info(f"Created new word with enrichment: {word_text}")
                except Exception as e:
                    logger.error(f"AI enrichment failed for word '{word_text}': {e}")
                    raise RuntimeError(f"AI enrichment failed for word '{word_text}': {e}")
            
            return word
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_or_create: {e}")
            raise
    
    @classmethod
    async def create_word(cls, word_data):
        """Create word from provided data"""
        try:
            word = await cls.get_by_word(word_data.word)

            if not word:
                word = await cls.create(
                    word=word_data.word,
                    level=word_data.level,
                    meaning=word_data.meaning,
                    example=word_data.example,
                    translation=word_data.translation
                )
                logger.info(f"Created word from data: {word_data.word}")
            
            return word
        except SQLAlchemyError as e:
            logger.error(f"Database error in create_word: {e}")
            raise