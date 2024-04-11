from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, KeyboardBuilder

from src.callback_factory import ProductCallbackFactory, CartCallbackFactory, OrderCallbackFactory
from src.config import CHANNEL_NAME, GROUP_NAME


def main_keyboard() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text='Каталог'),
         KeyboardButton(text='Корзина')],
         [KeyboardButton(text='Мои заказы'),
         KeyboardButton(text='F.A.Q')]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    return keyboard


def generate_category_keyboard(dict_category: dict, subcategory=False, current_page=1, category_id=0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    prefix = 'subcategory' if subcategory else 'category'
    for item in dict_category.items():
        builder.row(InlineKeyboardButton(text=item[1], callback_data=f'{prefix}_{item[0]}'), width=1)
    next_kb = InlineKeyboardButton(text='>>', callback_data=f'page_{prefix}{category_id}_{current_page + 1}')
    down_kb = InlineKeyboardButton(text='<<', callback_data=f'page_{prefix}{category_id}_{current_page - 1}')
    builder.row(down_kb, next_kb, width=2) if current_page > 1 else builder.row(next_kb, width=1)
    if prefix == 'subcategory':
        builder.row(InlineKeyboardButton(text='К категориям', callback_data='return_to_category'))
    return builder.as_markup()


def channel_keyboard() -> InlineKeyboardMarkup:
    button_url_channel = InlineKeyboardButton(text='Канал', url=f'https://t.me/{CHANNEL_NAME}')
    button_url_group = InlineKeyboardButton(text='Группа', url=f'https://t.me/{GROUP_NAME}')
    button_check = InlineKeyboardButton(text='Проверить', callback_data='check_subscribe')
    return InlineKeyboardBuilder().add(button_url_channel, button_url_group, button_check).adjust(1).as_markup()


def product_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='⬅️', callback_data=ProductCallbackFactory(action='back'))
    builder.button(text='➡️', callback_data=ProductCallbackFactory(action='next'))
    builder.button(text='В корзину', callback_data=ProductCallbackFactory(action='incart'))
    builder.button(text='К категориям', callback_data='return_to_category')
    return builder.adjust(2).as_markup()


def choose_quantity_keyboard(quantity=1) -> InlineKeyboardMarkup:
    quantity = 1 if quantity < 1 else quantity
    builder = InlineKeyboardBuilder()
    builder.button(text='-', callback_data=ProductCallbackFactory(action='incart-', quantity=quantity))
    builder.button(text=str(quantity), callback_data=ProductCallbackFactory(action='some'))
    builder.button(text='+', callback_data=ProductCallbackFactory(action='incart+', quantity=quantity))
    builder.button(text='Назад ◀️', callback_data=ProductCallbackFactory(action='return'))
    builder.button(text='Подтвердить ✅', callback_data=ProductCallbackFactory(action='saveincart', quantity=quantity))
    return builder.adjust(3).as_markup()


def cart_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='Оформить заказ ✅', callback_data=CartCallbackFactory(action='success'))
    builder.button(text='Удалить товар', callback_data=CartCallbackFactory(action='change'))
    return builder.adjust(1).as_markup()


def cart_changer_keyboard(lst_items, cart_id) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for el in lst_items:
        builder.button(text=el[1], callback_data=CartCallbackFactory(action='delete', product_id=el[0], cart_id=cart_id))
    builder.button(text='Очистить все' , callback_data=CartCallbackFactory(action='alldel', cart_id=cart_id))
    builder.button(text='Назад ◀️', callback_data=CartCallbackFactory(action='back'))
    return builder.adjust(1).as_markup()


def send_phone_keyboard() -> ReplyKeyboardMarkup:
    button_phone = KeyboardButton(text='Поделиться номером', request_contact=True)
    kb = [[button_phone]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def pay_keyboard() -> InlineKeyboardMarkup:
    button_pay = InlineKeyboardButton(text='Оплатить', pay=True)
    return InlineKeyboardBuilder().add(button_pay).adjust(1).as_markup()


def orders_keyboard(ids_orders) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for el in ids_orders:
        builder.button(text=f'Заказ №{el}', callback_data=OrderCallbackFactory(order_id=el))
    return builder.adjust(1).as_markup()


def delete_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Закрыть', callback_data='delete_message'))
    return builder.as_markup()




