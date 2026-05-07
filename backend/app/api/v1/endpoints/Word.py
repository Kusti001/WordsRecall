from fastapi import APIRouter, HTTPException
from app.repositories.WordRepository import WordRepository

from app.schemas import BaseResponse, WordResponse, ListResponse

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/words", tags=["words"])

@router.get("/{word}")
async def get_or_create(word: str) -> BaseResponse:
    """Get word details or create new one with AI enrichment"""
    try:
        res = await WordRepository.get_or_create(word)
        logger.info(f"Retrieved/created word: {word}")
        return BaseResponse(
            message="Word retrieved/created successfully",
            data=WordResponse(
                id=res.id,
                word=res.word,
                level=res.level,
                example=res.example,
                meaning=res.meaning,
                translation=res.translation
            )
        )
    except Exception as e:
        logger.error(f"Unexpected error getting word '{word}': {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("")
async def get_all_words() -> ListResponse:
    """Get all words in the database"""
    try:
        words = await WordRepository.get_all_words()
        logger.info(f"Retrieved {len(words)} words")
        return ListResponse(
            message="Words retrieved successfully",
            total=len(words),
            items=[WordResponse(
                id=word.id,
                word=word.word,
                level=word.level,
                example=word.example,
                meaning=word.meaning,
                translation=word.translation
            ) for word in words]
        )
    except Exception as e:
        logger.error(f"Unexpected error getting all words: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")