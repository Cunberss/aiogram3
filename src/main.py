import asyncio
from src.bot import bot, dp
from handlers.commands import router as commands_router
from handlers.messages import router as messages_router
from handlers.callbacks import router as callbacks_router
import logging
from loguru import logger

logger.add("logs/{time:YYYY-MM-DD}_logfile.log",
           format="{time} {level} {message}",
           level="DEBUG",
           rotation="00:00",
           compression="zip")


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__ and frame.f_code.co_name != "_log":
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


async def main():
    logging.getLogger('aiogram').setLevel(logging.DEBUG)
    logging.getLogger('aiogram').addHandler(InterceptHandler())
    logging.getLogger('asyncio').setLevel(logging.DEBUG)
    logging.getLogger('asyncio').addHandler(InterceptHandler())
    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_router(commands_router)
    dp.include_router(messages_router)
    dp.include_router(callbacks_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())