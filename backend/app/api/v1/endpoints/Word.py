from fastapi import APIRouter
from app.repositories.WordRepository import WordRepository


router = APIRouter(
    prefix="/words"
) # создаем экземпляр маршрутизатора APIRouter, который будет использоваться для определения маршрутов

@router.get("/{word}")
async def get_or_create(word: str):
    word_data = await WordRepository.get_or_create(word)
    return {
    "id": word_data.id,
    "word": word_data.word,
    "level": word_data.level,
    "example": word_data.example,
    "meaning": word_data.meaning,
    "translation": word_data.translation
}

@router.get("/get_all")
async def get_all_words():
    words = await WordRepository.get_all_words()
    return {"words": words}