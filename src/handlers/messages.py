from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, Contact
from sqlalchemy import select, insert, desc

from src.bot import bot
from src.db.models import User, Cart, Category, SubCategory, CartItem, Product
from src.db.base import get_session
from src.fsm import OrderCreate
from src.keyboards import main_keyboard, generate_category_keyboard, cart_keyboard
from src.config import PER_PAGE, BOT_USERNAME
from src.some_functions import generation_message_cartitems

router = Router(name='messages-router')


@router.message(F.text == 'Корзина')
async def user_cart_handler(message: Message, state: FSMContext):
    await state.clear()
    async with get_session() as session:
        query = select(Cart).where(Cart.user_id == message.from_user.id)
        result = await session.execute(query)
        answer = result.all()
        if answer:
            cart_id = answer[0][0].id
            query = select(Product.name, CartItem.quantity, (Product.price * CartItem.quantity).label('total_price')).join(CartItem, Product.id == CartItem.product_id).filter(CartItem.cart_id == cart_id).order_by(desc(CartItem.id))
            result = await session.execute(query)
            answer = result.all()
            if answer:
                lst_items = [el for el in answer]
                mes = generation_message_cartitems(lst_items)
                await bot.send_message(message.from_user.id, mes, reply_markup=cart_keyboard())
            else:
                await message.answer(f'Ваша корзина пуста')
        else:
            await message.answer(f'Ваша корзина пуста')


@router.message(F.text == 'Каталог')
async def catalog_handler(message: Message, state: FSMContext):
    await state.clear()
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
async def faq_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(f'Начни вводить @{BOT_USERNAME} для вызова F.A.Q...')


@router.message(OrderCreate.phone)
async def get_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    name = message.contact.first_name
    await state.set_state(OrderCreate.address)
    await state.update_data(phone=phone, name=name)
    await bot.send_message(message.from_user.id, 'Введите адрес доставки 👇', reply_markup=main_keyboard())


@router.message(OrderCreate.address)
async def get_address(message: Message, state: FSMContext):
    address = message.text
    if len(address) < 8 or len(address) > 120:
        await bot.send_message(message.from_user.id, 'Введите корректный адрес доставки 👇')
    else:
        data = await state.get_data()
        phone, name = data['phone'], data['name']
        await state.clear()




