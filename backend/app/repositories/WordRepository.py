from app.core.database import Word, new_session
from .base import BaseRepository
from sqlalchemy import select
from ..utils.word_enrichment import enrich_word_text

class WordRepository(BaseRepository[Word]):
    model = Word

    @classmethod
    async def get_by_word(cls, word_text: str):
        """get word by english text"""
        async with new_session() as session:
            query = select(Word).where(Word.word == word_text)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_all_words(cls):
        """get all words"""
        return await cls.get_all()

    @classmethod
    async def get_or_create(cls, word_text: str):
        """get word, if it doesn't exist — create it using the local Ollama model."""
        word = await cls.get_by_word(word_text)
        
        if not word:
            enriched = await enrich_word_text(word_text)
            word = await cls.create(
                word=enriched.word,
                level=enriched.level,
                meaning=enriched.meaning,
                example=enriched.example,
                translation=enriched.translation,
            )
        
        return word
    
    @classmethod
    async def create_word(cls, word_data):
        """get word by english text"""
        word = await cls.get_by_word(word_data.word)

        if not word:
            word = await cls.create(
                word=word_data.word,
                level=word_data.level,
                meaning=word_data.meaning,
                example=word_data.example,
                translation=word_data.translation
            )
            
        return word