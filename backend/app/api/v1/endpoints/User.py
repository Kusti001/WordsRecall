from fastapi import APIRouter, HTTPException
from app.repositories.UserRepository import UserRepository
from app.repositories.UserWordRepository import UserWordRepository

from app.schemas.User import UserCreate

import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])

# ============ USER ENDPOINTS ============

@router.post("")
async def create_user(body: UserCreate):
    """Create a new user (register in the bot)"""
    try:
        user = await UserRepository.get_by_telegram_id(body.telegram_id)
        
        if user:
            logger.info(f"User {body.telegram_id} already exists")
            return {"message": "user_already_exists"}
        
        await UserRepository.create_user(body.telegram_id)
        logger.info(f"User {body.telegram_id} created")
        return {"message": "user_created"}
    except Exception as e:
        logger.error(f"Unexpected error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{telegram_id}")
async def get_user(telegram_id: str):
    """Get user details by Telegram ID"""
    try:
        user = await UserRepository.get_by_telegram_id(telegram_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "user_id": user.id,
            "telegram_id": user.telegram_id,
            "created_at": user.created_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# в идеале перенести в обычный эндпоинт повторения !!!
@router.get("/{telegram_id}/words/new")
async def get_new_words(telegram_id: str):
    """Get new words for the user (that haven't been added to their dictionary yet)"""
    try:
        user = await UserRepository.get_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        new_user_words = await UserWordRepository.get_new_words(user.id)

        logger.info(f"Retrieved {len(new_user_words)} new words for user {telegram_id}")

        return {
            "total": len(new_user_words),
            "words": [
                {
                    "user_word_id": uw.id,
                    "word_id": uw.word_id,
                    "word": uw.word.word,
                    "translation": uw.word.translation,
                    "meaning": uw.word.meaning,
                    "example": uw.word.example,
                    "level": uw.word.level,
                }
                for uw in new_user_words
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting new words for user {telegram_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    
@router.get("/{telegram_id}/stats")
async def get_user_stats(telegram_id: str):
    """Get user statistics (total words, review performance, etc.)"""
    try:
        user = await UserRepository.get_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        stats = await UserWordRepository.get_user_stats(user.id)

        logger.info(f"Retrieved stats for user {telegram_id}")

        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting stats for user {telegram_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")