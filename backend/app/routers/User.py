from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..repositories.UserRepository import UserRepository
from ..repositories.WordRepository import WordRepository
from ..repositories.UserWordRepository import UserWordRepository
from ..repositories.ReviewRepository import ReviewRepository

from ..schemas.User import UserCreate
from ..schemas.UserWord import AddWordRequest

router = APIRouter(prefix="/users")

# ============ SCHEMAS ============


class ReviewSubmit(BaseModel):
    result: bool  # true = правильно, false = неправильно


# ============ USER ENDPOINTS ============

@router.post("")
async def create_user(body: UserCreate):
    """Создать нового пользователя (регистрация в боте)"""
    user = await UserRepository.get_by_telegram_id(body.telegram_id)
    
    if user:
        return {"user_id": user.id, "message": "user_already_exists"}
    
    user = await UserRepository.create_user(body.telegram_id)
    return {"user_id": user.id, "telegram_id": user.telegram_id}


@router.get("/{telegram_id}")
async def get_user(telegram_id: str):
    """Получить профиль пользователя"""
    user = await UserRepository.get_by_telegram_id(telegram_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user.id,
        "telegram_id": user.telegram_id,
        "created_at": user.created_at
    }


# ============ WORD MANAGEMENT ENDPOINTS ============

@router.post("/{telegram_id}/words")
async def add_word_to_user(telegram_id: str, body: AddWordRequest):
    """Добавить слово в список обучения"""
    # 1. Получаем пользователя
    user = await UserRepository.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 2. Получаем или создаём слово (через GPT если нужно)
    word = await WordRepository.get_or_create(body.text)
    
    # 3. Добавляем слово в список пользователя
    user_word = await UserWordRepository.add_word_to_user(user.id, word.id)
    
    if isinstance(user_word, dict) and "error" in user_word:
        return user_word  # уже добавлено
    
    return {
        "message": "word_added",
        "user_word_id": user_word.id,
        "word": word.word,             # ← английское слово
        "level": word.level,           # ← уровень сложности
        "translation": word.translation,  # ← русский перевод
        "meaning": word.meaning,       # ← определение
        "example": word.example        # ← пример
    }


@router.get("/{telegram_id}/words")
async def get_user_words(telegram_id: str):
    """Получить все слова пользователя"""
    user = await UserRepository.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_words = await UserWordRepository.get_user_all_words(user.id)
    
    return {
        "total": len(user_words),
        "words": [
            {
                "user_word_id": uw.id,
                "word": uw.word.word,
                "translation": uw.word.translation,
                "interval": uw.interval,
                "repetitions": uw.repetitions,
                "next_review": uw.next_review
            }
            for uw in user_words
        ]
    }


@router.delete("/{telegram_id}/words/{user_word_id}")
async def remove_word_from_user(telegram_id: str, user_word_id: int):
    """Удалить слово из списка"""
    user = await UserRepository.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await UserWordRepository.delete_user_word(user_word_id, user.id)
    
    return {"message": "word_removed"}


# ============ REVIEW ENDPOINTS ============

@router.get("/{telegram_id}/words/review")
async def get_review_words(telegram_id: str):
    """Получить слова, готовые к повторению"""
    user = await UserRepository.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_words = await UserWordRepository.get_review_words(user.id)
    
    return {
        "total": len(user_words),
        "words": [
            {
                "user_word_id": uw.id,
                "word": uw.word.word,           # показываем английское слово
                "translation": uw.word.translation,
                "example": uw.word.example,
                "interval": uw.interval,
                "repetitions": uw.repetitions,
                "next_review": uw.next_review
            }
            for uw in user_words
        ]
    }


@router.patch("/{telegram_id}/words/{user_word_id}/review")
async def submit_review(telegram_id: str, user_word_id: int, body: ReviewSubmit):
    """Отправить ответ на слово (правильно/неправильно)"""
    user = await UserRepository.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Обновляем метрики spaced repetition
    updated_uw = await UserWordRepository.update_review(user_word_id, body.result, user.id)
    
    # Логируем в Review таблицу
    await ReviewRepository.log_review(user_word_id, result="correct" if body.result else "incorrect")
    
    return {
        "message": "review_recorded",
        "user_word_id": user_word_id,
        "correct": body.result,
        "interval": updated_uw.interval,
        "repetitions": updated_uw.repetitions,
        "next_review": updated_uw.next_review
    }


# ============ STATS ENDPOINTS ============

@router.get("/{telegram_id}/stats")
async def get_user_stats(telegram_id: str):
    """Получить статистику пользователя"""
    user = await UserRepository.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    all_words = await UserWordRepository.get_user_all_words(user.id)
    review_words = await UserWordRepository.get_review_words(user.id)
    
    total_repetitions = sum(uw.repetitions for uw in all_words)
    
    return {
        "user_id": user.id,
        "telegram_id": user.telegram_id,
        "total_words": len(all_words),
        "ready_for_review": len(review_words),
        "total_correct_answers": total_repetitions,
        "created_at": user.created_at
    }