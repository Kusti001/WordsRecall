from fastapi import APIRouter, HTTPException
from app.repositories.UserRepository import UserRepository
from ....repositories.UserWordRepository import UserWordRepository
from ....repositories.ReviewRepository import ReviewRepository
from ....schemas.Review import ReviewRequest
from ....schemas.User import UserCreate
from ....schemas.UserWord import AddWordRequest

router = APIRouter(prefix="/users")

# ============ USER ENDPOINTS ============

@router.post("")
async def create_user(body: UserCreate):
    """Create a new user (register in the bot)"""
    user = await UserRepository.get_by_telegram_id(body.telegram_id)
    
    if user:
        return {"message": "user_already_exists"}
    
    user = await UserRepository.create_user(body.telegram_id)
    return {"message": "user_created"}


@router.get("/{telegram_id}")
async def get_user(telegram_id: str):
    """Get user details by Telegram ID"""
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
    """Add a word to the user's learning list"""
    # 1. Get the user
    user = await UserRepository.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 2. Add the word to the user's list (or return if already added)
    res = await UserWordRepository.add_word_to_user(user.id, body.id)
    
    return res



@router.delete("/{telegram_id}/words/{user_word_id}")
async def remove_word_from_user(telegram_id: str, user_word_id: int):
    """Remove a word from the user's learning list"""
    user = await UserRepository.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await UserWordRepository.delete_user_word(user_word_id, user.id)
    
    return {"message": "word_removed"}


# ============ REVIEW ENDPOINTS ============

@router.get("/{telegram_id}/words/review")
async def get_review_words(telegram_id: str):
    """Get words ready for review"""
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
                "meaning": uw.word.meaning,
                "example": uw.word.example,
                "level": uw.word.level,
            }
            for uw in user_words
        ]
    }

@router.post("/{telegram_id}/words/{user_word_id}/review")
async def review_word(telegram_id: str, user_word_id: int, body: ReviewRequest):
    """Оценить слово после повторения — обновляет дату следующего повторения"""
    user = await UserRepository.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    res = await ReviewRepository.log_review(user_word_id, body.result)
    
        # Обновляем интервалы повторения
    await UserWordRepository.update_review(user_word_id, body.result)
    
    return res