from fastapi import APIRouter, Depends
from typing import Annotated
from ..schemas.Word import WordAdd
from ..repositories.WordRepository import WordRepository


router = APIRouter(
    prefix="/words"
) # создаем экземпляр маршрутизатора APIRouter, который будет использоваться для определения маршрутов



@router.post("")
async def add_word(word: Annotated[WordAdd, Depends()]):
    word_id = await WordRepository.add_word(word)
    return {"word_id": word_id} # определяем маршрут /add_word, который возвращает JSON-ответ с сообщением "Hello World!"

@router.get("/get_all")
async def get_all_words():
    words = await WordRepository.get_all_words()
    return {"words": words} # определяем маршрут /get_all_words, который возвращает JSON-ответ с сообщением "Hello World!"