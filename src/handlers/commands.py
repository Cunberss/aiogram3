from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy import select, insert
from src.db.models import User
from src.db.base import get_session
from src.keyboards import main_keyboard, channel_keyboard
from src.bot import bot
from src.config import CHANNEL_NAME, GROUP_NAME

router = Router(name='commands-router')


@router.message(CommandStart())
async def cmd_start(message: Message):
    async with get_session() as session:
        user_exists = await session.get(User, message.from_user.id)
        if not user_exists:
            stmt = insert(User).values(user_id=message.from_user.id, username=message.from_user.username)
            await session.execute(stmt)
            await session.commit()
    user_channel_status = await bot.get_chat_member(chat_id=f'@{CHANNEL_NAME}', user_id=message.from_user.id)
    user_group_status = await bot.get_chat_member(chat_id=f'@{GROUP_NAME}', user_id=message.from_user.id)
    if user_channel_status.status != 'left' and user_group_status.status != 'left':
        await message.answer(f'Привет, {message.from_user.username}!', reply_markup=main_keyboard())
    else:
        await message.answer('Для продолжения, подпишись на канал и вступи в группу', reply_markup=channel_keyboard())

