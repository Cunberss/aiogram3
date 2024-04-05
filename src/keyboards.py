from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, KeyboardBuilder


def main_keyboard() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text='Каталог'),
         KeyboardButton(text='Корзина'),
         KeyboardButton(text='F.A.Q')]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    return keyboard


def generate_category_keyboard(dict_category: dict, subcategory=False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    prefix = 'subcategory' if subcategory else 'category'
    for item in dict_category.items():
        builder.add(InlineKeyboardButton(text=item[1], callback_data=f'{prefix}_{item[0]}'))
    return builder.adjust(1).as_markup()
