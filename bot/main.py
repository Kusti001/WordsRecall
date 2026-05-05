import asyncio
import logging
from aiogram import Bot, Dispatcher
from handlers import router
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point for the bot"""
    logger.info("Starting bot...")
    
    try:
        bot = Bot(token=settings.BOT_TOKEN)
        dp = Dispatcher()
        dp.include_router(router)
        
        logger.info("Bot initialized successfully")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
