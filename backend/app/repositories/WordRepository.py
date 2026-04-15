from app.core.database import Word, new_session
from .base import BaseRepository
from sqlalchemy import select

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
            pass
        
        return word
    
    @classmethod
    async def create_word(cls, word_data):
        """Добавить новое слово в базу данных"""
        from sqlalchemy.exc import IntegrityError
        
        try:
            word = await cls.create(
                word=word_data.word,
                level=word_data.level,
                meaning=word_data.meaning,
                example=word_data.example,
                translation=word_data.translation
            )
            return word.id
        except IntegrityError:
            # Слово уже существует - возвращаем его ID
            existing = await cls.get_by_word(word_data.word)
            if existing:
                return existing.id
            raise