from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select, insert
from src.db.models import User, Cart, Category, SubCategory
from src.db.base import get_session
from src.keyboards import main_keyboard, generate_category_keyboard

router = Router(name='messages-router')


@router.message(F.text == 'Корзина')
async def user_cart_handler(message: Message):
    async with get_session() as session:
        query = select(Cart).where(Cart.user_id == message.from_user.id)
        result = await session.execute(query)
        if result.all():
            pass
        else:
            await message.answer(f'Ваша корзина пуста')


@router.message(F.text == 'Каталог')
async def catalog_handler(message: Message):
    async with get_session() as session:
        query = select(Category)
        result = await session.execute(query)
        answer = result.all()
        if answer:
            categories_dict = {el[0].id: el[0].name for el in answer}
            await message.answer('Выбери категорию', reply_markup=generate_category_keyboard(categories_dict))
        else:
            await message.answer(f'Каталог пуст')
