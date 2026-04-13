from app.core.database import Word, new_session
from .base import BaseRepository
from sqlalchemy import select
from ..services.gpt import generate_word_data

class WordRepository(BaseRepository[Word]):
    model = Word

    @classmethod
    async def get_by_word(cls, word_text: str):
        """Получить слово по тексту"""
        async with new_session() as session:
            query = select(Word).where(Word.word == word_text)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_all_words(cls):
        """Получить все слова"""
        return await cls.get_all()

    @classmethod
    async def get_or_create(cls, word_text: str):
        """Получить слово, если не существует — создать через GPT"""
        word = await cls.get_by_word(word_text)
        
        if not word:
            # Генерируем данные через GPT
            word_data = await generate_word_data(word_text)  # async!
            word = await cls.create(
                word=word_text,
                translation=word_data["translation"],
                meaning=word_data.get("meaning"),
                example=word_data.get("example")
            )
        
        return word

    @classmethod
    async def bulk_create(cls, words_list: list[dict]):
        """Пакетная загрузка слов"""
        async with new_session() as session:
            for word_data in words_list:
                word = Word(**word_data)
                session.add(word)
            await session.commit()