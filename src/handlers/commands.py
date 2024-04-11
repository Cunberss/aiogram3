from datetime import datetime

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile

from src.db.functions import db_add_user
from src.keyboards import main_keyboard, channel_keyboard
from src.bot import bot
from src.config import CHANNEL_NAME, GROUP_NAME, MANAGER_ID

router = Router(name='commands-router')


@router.message(CommandStart())
async def cmd_start(message: Message):
    await db_add_user(message.from_user.id, message.from_user.username)
    user_channel_status = await bot.get_chat_member(chat_id=f'@{CHANNEL_NAME}', user_id=message.from_user.id)
    user_group_status = await bot.get_chat_member(chat_id=f'@{GROUP_NAME}', user_id=message.from_user.id)
    if user_channel_status.status != 'left' and user_group_status.status != 'left':
        await message.answer(f'Привет, {message.from_user.username}!', reply_markup=main_keyboard())
    else:
        await message.answer('Для продолжения, подпишись на канал и вступи в группу', reply_markup=channel_keyboard())


@router.message(Command('orders'))
async def get_orders_manager_handler(message: Message):
    if int(message.from_user.id) == int(MANAGER_ID):
        date = datetime.now().strftime('%Y-%m-%d')
        filename = f'orders/order_{date}.xlsx'
        try:
            file = FSInputFile(filename)
            await bot.send_document(message.from_user.id, document=file, caption='Заказы за сегодня')
        except Exception:
            await bot.send_message(message.from_user.id, 'Заказов сегодня не было')


