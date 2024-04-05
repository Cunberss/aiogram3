import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.commands import router as commands_router
from handlers.messages import router as messages_router
from handlers.callbacks import router as callbacks_router


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_router(commands_router)
    dp.include_router(messages_router)
    dp.include_router(callbacks_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())