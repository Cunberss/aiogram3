from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select, insert
from src.db.models import User, Cart, Category, SubCategory
from src.db.base import get_session
from src.keyboards import main_keyboard, generate_category_keyboard
from src.config import PER_PAGE, BOT_USERNAME

router = Router(name='messages-router')


@router.message(F.text == 'Корзина')
async def user_cart_handler(message: Message):
    async with get_session() as session:
        query = select(Cart).order_by(Cart.id).where(Cart.user_id == message.from_user.id)
        result = await session.execute(query)
        if result.all():
            pass
        else:
            await message.answer(f'Ваша корзина пуста')


@router.message(F.text == 'Каталог')
async def catalog_handler(message: Message):
    async with get_session() as session:
        page = 1
        start = (page - 1) * PER_PAGE
        end = start + PER_PAGE
        query = select(Category).slice(start, end)
        result = await session.execute(query)
        answer = result.all()
        if answer:
            categories_dict = {el[0].id: el[0].name for el in answer}
            await message.answer('Выбери категорию', reply_markup=generate_category_keyboard(categories_dict, current_page=page))
        else:
            await message.answer(f'Каталог пуст')


@router.message(F.text == 'F.A.Q')
async def faq_handler(message: Message):
    await message.answer(f'Начни вводить @{BOT_USERNAME} для вызова F.A.Q...')
