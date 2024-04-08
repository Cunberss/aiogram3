from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, KeyboardBuilder
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
    return builder.as_markup()


def channel_keyboard() -> InlineKeyboardMarkup:
    button_url_channel = InlineKeyboardButton(text='Канал', url=f'https://t.me/{CHANNEL_NAME}')
    button_url_group = InlineKeyboardButton(text='Группа', url=f'https://t.me/{GROUP_NAME}')
    button_check = InlineKeyboardButton(text='Проверить', callback_data='check_subscribe')
    return InlineKeyboardBuilder().add(button_url_channel, button_url_group, button_check).adjust(1).as_markup()


def product_keyboard() -> InlineKeyboardMarkup:
    button_back = InlineKeyboardButton(text='⬅️', callback_data='product_back')
    button_next = InlineKeyboardButton(text='➡️', callback_data='product_next')
    button_cart = InlineKeyboardButton(text='В корзину', callback_data='product_incart')
    return InlineKeyboardBuilder().add(button_back,button_next, button_cart).adjust(2).as_markup()


def choose_quantity_keyboard(quantity=1) -> InlineKeyboardMarkup:
    quantity = 1 if quantity < 1 else quantity
    button_left = InlineKeyboardButton(text='-', callback_data=f'product_incart-_{quantity}')
    button_right = InlineKeyboardButton(text='+', callback_data=f'product_incart+_{quantity}')
    button_quantity = InlineKeyboardButton(text=str(quantity), callback_data='product_some')
    button_back = InlineKeyboardButton(text='Назад ◀️', callback_data='product_return')
    button_success = InlineKeyboardButton(text='Подтвердить ✅', callback_data=f'product_saveincart_{quantity}')
    return InlineKeyboardBuilder().add(button_left, button_quantity, button_right, button_back, button_success).adjust(3).as_markup()


def cart_keyboard() -> InlineKeyboardMarkup:
    button_success = InlineKeyboardButton(text='Оформить заказ ✅', callback_data='cart_success')
    button_change = InlineKeyboardButton(text='Удалить товар', callback_data='cart_change')
    return InlineKeyboardBuilder().add(button_success, button_change).adjust(1).as_markup()


def cart_changer_keyboard(lst_items, cart_id) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for el in lst_items:
        builder.row(InlineKeyboardButton(text=el[1], callback_data=f'cart_delete_{el[0]}_{cart_id}'), width=1)
    builder.row(InlineKeyboardButton(text='Очистить все' , callback_data=f'cart_alldel_{cart_id}'))
    builder.row(InlineKeyboardButton(text='Назад ◀️', callback_data=f'cart_back'))
    return builder.as_markup()


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
        builder.row(InlineKeyboardButton(text=f'Заказ №{el}', callback_data=f'checkorder_{el}'), width=1)
    return builder.as_markup()


def delete_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Закрыть', callback_data='delete_message'))
    return builder.as_markup()




