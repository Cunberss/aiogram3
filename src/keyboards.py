from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, KeyboardBuilder
from src.config import CHANNEL_NAME, GROUP_NAME


def main_keyboard() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text='Каталог'),
         KeyboardButton(text='Корзина'),
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

