from fastapi import APIRouter, HTTPException
from app.repositories.UserRepository import UserRepository
from app.repositories.UserWordRepository import UserWordRepository
from app.repositories.ReviewRepository import ReviewRepository

from app.schemas.Review import ReviewRequest
from app.schemas import BaseResponse

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/{telegram_id}/{user_word_id}")
async def review_word(telegram_id: str, user_word_id: int, body: ReviewRequest) -> BaseResponse:
    """Record review result and update next review interval"""
    try:
        user = await UserRepository.get_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        review = await ReviewRepository.log_review(user_word_id, body.result)
        logger.info(f"Review logged for user {telegram_id}, word {user_word_id}: {body.result}")
        
        # Update learning interval based on result
        await UserWordRepository.update_review(user_word_id, body.result)
        
        return BaseResponse(message="Review recorded successfully")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error recording review: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")