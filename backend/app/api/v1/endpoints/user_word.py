from fastapi import APIRouter, HTTPException
from app.repositories.UserRepository import UserRepository
from app.repositories.UserWordRepository import UserWordRepository

from app.schemas.UserWord import AddOrDeleteWordRequest
from app.schemas.Response import BaseResponse, ListResponse, UserWordResponse

import logging
from app.schemas.Response import BaseResponse, ListResponse, UserWordResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["user_words"])

    
@router.get("/{telegram_id}/words")
async def get_user_dictionary(telegram_id: str) -> ListResponse:
    """Get user's complete dictionary"""
    try:
        user = await UserRepository.get_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_words = await UserWordRepository.get_user_dictionary(user.id)
        
        return ListResponse(
            message="User dictionary retrieved successfully",
            total=len(user_words),
            items=[
                {
                    "word": uw.word.word,
                    "translation": uw.word.translation,
                    "next_review": uw.next_review.strftime("%d.%m.%Y - %H:%M:%S"),
                }
                for uw in user_words
            ]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting dictionary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@router.post("/{telegram_id}/words")
async def add_word_to_user(telegram_id: str, body: AddOrDeleteWordRequest) -> BaseResponse:
    """Add a word to the user's learning list"""
    try:
        user = await UserRepository.get_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        res = await UserWordRepository.add_word_to_user(user.id, body.word_id)
        
        if res["status"] == "already_exists":
            logger.info(f"Word {res['word']} already exists for user {telegram_id}")
            return BaseResponse(message="word_already_exists", data={
                "word": res["word"],
                "translation": res["translation"],
                "meaning": res["meaning"],
                "example": res["example"],
                "level": res["level"]
            })
        else:
            logger.info(f"Word {res['word']} added for user {telegram_id}")
            return BaseResponse(message="word_added", data=UserWordResponse(
                user_word_id=res["user_word_id"],
                word=res["word"],
                translation=res["translation"],
                meaning=res["meaning"],
                example=res["example"],
                level=res["level"]
            ))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error adding word: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")    

@router.delete("/{telegram_id}/words/{word_id}")
async def remove_word_from_user(telegram_id: str, word_id: str) -> BaseResponse:
    """Remove a word from the user's learning list"""
    try:
        user = await UserRepository.get_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        await UserWordRepository.delete_user_word(word_id, user.id)
        logger.info(f"Word {word_id} removed for user {telegram_id}")
        return BaseResponse(message="Word removed successfully")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error removing word: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{telegram_id}/words", status_code=200)
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
    
#SPECIFIC ENDPOINTS

@router.get("/{telegram_id}/words/review")
async def get_review_words(telegram_id: str) -> ListResponse:
    """Get words ready for review"""
    try:
        user = await UserRepository.get_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_words = await UserWordRepository.get_review_words(user.id)
        logger.info(f"Retrieved {len(user_words)} review words for user {telegram_id}")
        
        return  ListResponse(
            message="Review words retrieved successfully",
            total=len(user_words),
            items=[
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
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting review words: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{telegram_id}/words/new")
async def get_new_words(telegram_id: str) -> ListResponse:
    """Get new words for the user (that haven't been added to their dictionary yet)"""
    try:
        user = await UserRepository.get_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        new_user_words = await UserWordRepository.get_new_words(user.id)

        logger.info(f"Retrieved {len(new_user_words)} new words for user {telegram_id}")

        words_data = [
            UserWordResponse(
                user_word_id=uw.id,
                word=uw.word.word,
                translation=uw.word.translation,
                meaning=uw.word.meaning,
                example=uw.word.example,
                level=uw.word.level,
            )
            for uw in new_user_words
        ]
        
        return ListResponse(message="new_words_retrieved", total=len(words_data), items=words_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting new words for user {telegram_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")