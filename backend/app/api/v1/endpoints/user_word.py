from fastapi import APIRouter, HTTPException
from app.repositories.UserRepository import UserRepository
from app.repositories.UserWordRepository import UserWordRepository
from app.schemas.UserWord import AddWordRequest

import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])

@router.post("/{telegram_id}/words")
async def add_word_to_user(telegram_id: str, body: AddWordRequest):
    """Add a word to the user's learning list"""
    try:
        user = await UserRepository.get_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Add the word to the user's list (or return error if already added)
        res = await UserWordRepository.add_word_to_user(user.id, body.id)
        logger.info(f"Word added for user {telegram_id}: {res['word']}")
        return res
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error adding word: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.delete("/{telegram_id}/words/{user_word_id}")
async def remove_word_from_user(telegram_id: str, user_word_id: int):
    """Remove a word from the user's learning list"""
    try:
        user = await UserRepository.get_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        await UserWordRepository.delete_user_word(user_word_id, user.id)
        logger.info(f"Word {user_word_id} removed for user {telegram_id}")
        return {"message": "word_removed"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error removing word: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/{telegram_id}/words/review")
async def get_review_words(telegram_id: str):
    """Get words ready for review"""
    try:
        user = await UserRepository.get_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_words = await UserWordRepository.get_review_words(user.id)
        logger.info(f"Retrieved {len(user_words)} review words for user {telegram_id}")
        
        return {
            "total": len(user_words),
            "words": [
                {
                    "user_word_id": uw.id,
                    "word": uw.word.word,
                    "translation": uw.word.translation,
                    "meaning": uw.word.meaning,
                    "example": uw.word.example,
                    "level": uw.word.level,
                }
                for uw in user_words
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting review words: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@router.get("/{telegram_id}/words/dictionary")
async def get_user_dictionary(telegram_id: str):
    """Get user's complete dictionary"""
    try:
        user = await UserRepository.get_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_words = await UserWordRepository.get_user_dictionary(user.id)
        
        return {
            "total": len(user_words),
            "words": [
                {
                    "word": uw.word.word,
                    "translation": uw.word.translation,
                    "next_review": uw.next_review.strftime("%d.%m.%Y"),
                }
                for uw in user_words
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting dictionary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    


@router.delete("/{telegram_id}/words/all", status_code=200)
async def delete_all_user_words(telegram_id: str):
    """
    Удалить ВСЕ слова из словаря пользователя
    """
    try:
        user = await UserRepository.get_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        code = await UserWordRepository.delete_all_user_words(user.id)

        return {
            "status": "success",
            "message": "Все слова успешно удалены",
            "code": code
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting all words: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")