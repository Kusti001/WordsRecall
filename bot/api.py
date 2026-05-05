# bot/api.py
import os
import re
import aiohttp
import asyncio
import logging

logger = logging.getLogger(__name__)
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

async def _api_request(method: str, endpoint: str, json: dict = None):
    """Make API request with error handling"""
    url = f"{BASE_URL}{endpoint}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, json=json, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status == 404:
                    logger.warning(f"API endpoint not found: {method} {url}")
                    return {"error": "not_found", "status_code": 404}
                elif r.status == 400:
                    logger.warning(f"Bad request: {method} {url}")
                    return {"error": "bad_request", "status_code": 400}
                elif r.status >= 500:
                    logger.error(f"Server error {r.status}: {method} {url}")
                    return {"error": "server_error", "status_code": r.status}
                
                return await r.json()
    except aiohttp.ClientConnectorError as e:
        logger.error(f"Cannot connect to API at {BASE_URL}: {e}")
        return {"error": "connection_failed", "message": "Backend server is not available"}
    except aiohttp.ClientSSLError as e:
        logger.error(f"SSL error connecting to {BASE_URL}: {e}")
        return {"error": "ssl_error", "message": "SSL verification failed"}
    except asyncio.TimeoutError:
        logger.error(f"Request timeout: {method} {url}")
        return {"error": "timeout", "message": "Backend server is not responding"}
    except aiohttp.ClientError as e:
        logger.error(f"HTTP client error: {e}")
        return {"error": "http_error", "message": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error in API request: {e}")
        return {"error": "unexpected", "message": str(e)}

async def register_user(telegram_id: str):
    """Register a new user"""
    return await _api_request("POST", "/users", {"telegram_id": telegram_id})

async def get_review(telegram_id: str):
    """Get words ready for review"""
    return await _api_request("GET", f"/users/{telegram_id}/words/review")
        
async def get_word(word: str):
    """Get word details or create new word"""
    return await _api_request("GET", f"/words/{word}")

async def add_word(telegram_id: str, word_id: str):
    """Add word to user's dictionary"""
    return await _api_request("POST", f"/reviews/{telegram_id}/words", {"id": word_id})

async def send_review(telegram_id: str, user_word_id: str, result: str):
    """Record word review result"""
    return await _api_request("POST", f"/users/{telegram_id}/words/{user_word_id}/review", {"result": result})

async def get_dictionary(telegram_id: str):
    """Get user's complete dictionary"""
    return await _api_request("GET", f"/users/{telegram_id}/words/dictionary")

async def get_new_words(telegram_id: str):
    """Get new words for the user"""
    return await _api_request("GET", f"/users/{telegram_id}/words/new")

async def get_stats(telegram_id: str):
    """Get user statistics"""
    return await _api_request("GET", f"/users/{telegram_id}/stats")


def is_valid_word(text: str) -> bool:
    text = text.strip()
    
    # Слишком длинное — это не слово
    if len(text) > 30:
        return False
    
    # Содержит цифры
    if any(c.isdigit() for c in text):
        return False
    
    # Содержит не-буквенные символы (кроме дефиса)
    if not re.match(r'^[a-zA-Z\-]+$', text):
        return False
    
    # Слишком короткое
    if len(text) < 2:
        return False
    
    return True

def escape_md(text: str) -> str:
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)