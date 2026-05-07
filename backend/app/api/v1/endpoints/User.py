from fastapi import APIRouter, HTTPException
from app.repositories.UserRepository import UserRepository
from app.repositories.UserWordRepository import UserWordRepository

from app.schemas.User import UserCreate
from app.schemas import BaseResponse, UserResponse

import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


@router.post("")
async def create_user(body: UserCreate) -> BaseResponse:
    """Create a new user (register in the bot)"""
    try:
        user = await UserRepository.get_by_telegram_id(body.telegram_id)
        
        if user:
            logger.info(f"User {body.telegram_id} already exists")
            return BaseResponse(message="user_already_exists", data=None)
        
        await UserRepository.create_user(body.telegram_id)
        logger.info(f"User {body.telegram_id} created")
        return BaseResponse(message="user_created", data=None)
    
    except Exception as e:
        logger.error(f"Unexpected error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{telegram_id}")
async def get_user(telegram_id: str) -> BaseResponse:
    """Get user details by Telegram ID"""
    try:
        user = await UserRepository.get_by_telegram_id(telegram_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = UserResponse(
            user_id=user.id,
            telegram_id=user.telegram_id,
            created_at=user.created_at.isoformat()
        )
        return BaseResponse(message="user_found", data=user_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    
@router.get("/{telegram_id}/stats")
async def get_user_stats(telegram_id: str) -> BaseResponse:
    """Get user statistics (total words, review performance, etc.)"""
    try:
        user = await UserRepository.get_by_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        stats = await UserWordRepository.get_user_stats(user.id)

        logger.info(f"Retrieved stats for user {telegram_id}")

        return BaseResponse(message="user_stats_retrieved", data=stats)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting stats for user {telegram_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")