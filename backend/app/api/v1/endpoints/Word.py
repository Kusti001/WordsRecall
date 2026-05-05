from fastapi import APIRouter, HTTPException, status
from app.repositories.WordRepository import WordRepository
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/words", tags=["words"])

@router.get("/{word}")
async def get_or_create(word: str):
    """Get word details or create new one with AI enrichment"""
    try:
        word_data = await WordRepository.get_or_create(word)
        logger.info(f"Retrieved/created word: {word}")
        return {
            "id": word_data.id,
            "word": word_data.word,
            "level": word_data.level,
            "example": word_data.example,
            "meaning": word_data.meaning,
            "translation": word_data.translation
        }
    except Exception as e:
        logger.error(f"Unexpected error getting word '{word}': {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/get_all")
async def get_all_words():
    """Get all words in the database"""
    try:
        words = await WordRepository.get_all_words()
        logger.info(f"Retrieved {len(words)} words")
        return {"words": words}
    except Exception as e:
        logger.error(f"Unexpected error getting all words: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")