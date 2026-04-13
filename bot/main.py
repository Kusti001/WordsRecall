import asyncio
from aiogram import Bot, Dispatcher
from handlers import router

BOT_TOKEN = "8651197013:AAF1o1d4m8bqdfTBEJEYNMZlUKwUGvTI7UM"

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())