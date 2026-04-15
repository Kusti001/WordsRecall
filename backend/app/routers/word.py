from fastapi import APIRouter
from ..schemas.Word import WordAdd
from ..repositories.WordRepository import WordRepository


router = APIRouter(
    prefix="/words"
) # создаем экземпляр маршрутизатора APIRouter, который будет использоваться для определения маршрутов



@router.post("")
async def create_word(word: WordAdd):
    try:
        word_id = await WordRepository.create_word(word)
        return {"word_id": word_id, "status": "success"}
    except Exception as e:
        # Обрабатываем ошибки без 500 ошибок сервера
        return {"status": "error", "message": str(e)}

@router.get("/get_all")
async def get_all_words():
    words = await WordRepository.get_all_words()
    return {"words": words}