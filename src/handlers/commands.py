from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy import select, insert
from src.db.models import User
from src.db.base import get_session
from src.keyboards import main_keyboard

router = Router(name='commands-router')


@router.message(CommandStart())
async def cmd_start(message: Message):
    async with get_session() as session:
        user_exists = await session.get(User, message.from_user.id)
        if not user_exists:
            stmt = insert(User).values(user_id=message.from_user.id, username=message.from_user.username)
            await session.execute(stmt)
            await session.commit()
    await message.answer(f'Привет, {message.from_user.username}!', reply_markup=main_keyboard())

