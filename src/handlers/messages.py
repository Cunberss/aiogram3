import os.path
from datetime import datetime

import pandas as pd
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, PreCheckoutQuery

from src.bot import bot
from src.db.functions import db_get_cart, db_get_cartitems, db_get_paid_orders, db_get_categories, db_update_phone, \
    db_get_cartitems_short, db_create_order, db_delete_cart, db_update_status_order, db_get_data_order
from src.fsm import OrderCreate
from src.keyboards import main_keyboard, generate_category_keyboard, cart_keyboard, pay_keyboard, orders_keyboard
from src.config import BOT_USERNAME, TOKEN_KASSA, MANAGER_ID
from src.some_functions import generation_message_cartitems, generation_order_data

router = Router(name='messages-router')


@router.message(F.text == 'Корзина')
async def user_cart_handler(message: Message, state: FSMContext):
    await state.clear()
    cart_id = await db_get_cart(message.from_user.id)
    answer = await db_get_cartitems(cart_id)
    if answer:
        lst_items = [el for el in answer]
        mes = generation_message_cartitems(lst_items)
        await bot.send_message(message.from_user.id, mes, reply_markup=cart_keyboard())
    else:
        await message.answer('Ваша корзина пуста')


@router.message(F.text == 'Мои заказы')
async def orders_handler(message: Message, state: FSMContext):
    await state.clear()
    answer = await db_get_paid_orders(message.from_user.id)
    if answer:
        lst_orders = [el for el in answer]
        ids_orders = [el[0] for el in answer]
        text = 'Ваши 5 последних заказов 👇\n\n'
        for el in lst_orders:
            text += f'№:{el[0]}, Стоимость: {el[1]}р, Адрес: {el[2]}\n'
        await bot.send_message(message.from_user.id, text=text, reply_markup=orders_keyboard(ids_orders))
    else:
        await message.answer('У вас еще нет оплаченных заказов')


@router.message(F.text == 'Каталог')
async def catalog_handler(message: Message, state: FSMContext):
    await state.clear()
    answer = await db_get_categories()
    if answer:
        categories_dict = {el[0].id: el[0].name for el in answer}
        await message.answer('Выбери категорию', reply_markup=generate_category_keyboard(categories_dict, current_page=1))
    else:
        await message.answer(f'Каталог пуст')


@router.message(F.text == 'F.A.Q')
async def faq_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(f'Начни вводить @{BOT_USERNAME} для вызова F.A.Q...')


@router.message(OrderCreate.phone)
async def get_contact(message: Message, state: FSMContext):
    await db_update_phone(message.from_user.id, message.contact.phone_number)
    await state.set_state(OrderCreate.address)
    await bot.send_message(message.from_user.id, 'Введите адрес доставки 👇', reply_markup=main_keyboard())


@router.message(OrderCreate.address)
async def get_address(message: Message, state: FSMContext):
    address = message.text
    if len(address) < 8 or len(address) > 120:
        await bot.send_message(message.from_user.id, 'Введите корректный адрес доставки 👇')
    else:
        cart_id = await db_get_cart(message.from_user.id)
        answer = await db_get_cartitems_short(cart_id)
        data_products = [f'product_id:{el[0]},quantity:{el[1]}' for el in answer]
        products = '\n'.join(data_products)
        price = sum([el[2] for el in answer])

        order_id = await db_create_order(message.from_user.id, address, price, products)
        await db_delete_cart(message.from_user.id, cart_id)

        await bot.send_invoice(chat_id=message.from_user.id,
                                   title='Тайтл заказа',
                                   description='Описание заказа',
                                   payload=f'order_id:{order_id}',
                                   provider_token=TOKEN_KASSA,
                                   currency='RUB',
                                   prices=[{'label': el[3], 'amount': int(el[2]) * 100} for el in answer],
                                   reply_markup=pay_keyboard())
        await state.clear()


@router.pre_checkout_query()
async def proccess_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def success_payment(message: Message):
    order_id = int(message.successful_payment.invoice_payload.split(':')[1])
    await db_update_status_order(order_id)
    await bot.send_message(message.from_user.id, 'Оплата прошла успешно! С вами свяжется менеджер в ближайшее время '
                                                 'для уточнения деталей доставки')
    await bot.send_message(MANAGER_ID, '‼️Пришел новый заказ ‼️')

    date = datetime.now().strftime('%Y-%m-%d')
    filename = f'orders/order_{date}.xlsx'

    answer = await db_get_data_order(order_id)
    new_data = [{'user_id': answer[0], 'username': answer[1], 'phone': answer[2], 'order_id': answer[3], 'price': answer[4]}]

    new_data[0]['data_order'] = await generation_order_data(answer, order_id)

    new_df = pd.DataFrame(new_data)
    if os.path.isfile(filename):
        df = pd.read_excel(filename)
        df = pd.concat([df, new_df], ignore_index=True)
    else:
        df = new_df
    df.to_excel(filename, index=False)








