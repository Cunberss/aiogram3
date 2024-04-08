from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, Contact
from sqlalchemy import select, insert, desc, update, and_, delete

from src.bot import bot
from src.db.models import User, Cart, Category, SubCategory, CartItem, Product, Order
from src.db.base import get_session
from src.fsm import OrderCreate
from src.keyboards import main_keyboard, generate_category_keyboard, cart_keyboard, pay_keyboard
from src.config import PER_PAGE, BOT_USERNAME, TOKEN_KASSA
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
    async with get_session() as session:
        query = update(User).where(User.user_id == message.from_user.id).values(phone=phone)
        await session.execute(query)
        await session.commit()
    await state.set_state(OrderCreate.address)
    await state.update_data(phone=phone)
    await bot.send_message(message.from_user.id, 'Введите адрес доставки 👇', reply_markup=main_keyboard())


@router.message(OrderCreate.address)
async def get_address(message: Message, state: FSMContext):
    address = message.text
    if len(address) < 8 or len(address) > 120:
        await bot.send_message(message.from_user.id, 'Введите корректный адрес доставки 👇')
    else:
        data = await state.get_data()
        phone = data['phone']
        await state.clear()
        async with get_session() as session:
            query = select(Cart).where(Cart.user_id == message.from_user.id)
            result = await session.execute(query)
            cart_id = int(result.all()[0][0].id)
            query = select(CartItem.product_id, CartItem.quantity, (Product.price * CartItem.quantity).label('total_price'), Product.name).join(CartItem, Product.id == CartItem.product_id).filter(CartItem.cart_id == cart_id).order_by(desc(CartItem.id))
            result = await session.execute(query)
            answer = result.all()
            data_products = [f'product_id:{el[0]},quantity:{el[1]}' for el in answer]
            products = '\n'.join(data_products)
            price = sum([el[2] for el in answer])
            query = insert(Order).values(user_id=message.from_user.id, address=address, price=price, products=products)
            await session.execute(query)
            await session.commit()
            query = select(Order.id).where(and_(Order.user_id == message.from_user.id, Order.status == False)).order_by(desc(Order.id))
            result = await session.execute(query)
            order_id = result.all()[0][0]
            query = delete(CartItem).where(CartItem.cart_id == cart_id)
            await session.execute(query)
            query = delete(Cart).where(Cart.user_id == message.from_user.id)
            await session.execute(query)
            await session.commit()
            await bot.send_invoice(chat_id=message.from_user.id,
                                   title='Тайтл заказа',
                                   description='Описание заказа',
                                   payload=f'order_id:{order_id}',
                                   provider_token=TOKEN_KASSA,
                                   currency='RUB',
                                   prices=[{'label': el[3], 'amount': int(el[2]) * 100} for el in answer],
                                   reply_markup=pay_keyboard())



