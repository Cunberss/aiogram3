from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, insert

from src.bot import bot
from src.config import CHANNEL_NAME, GROUP_NAME, PER_PAGE
from src.db.models import User, Cart, Category, SubCategory, Product
from src.db.base import get_session
from src.keyboards import main_keyboard, generate_category_keyboard

router = Router(name='callbacks-router')


@router.callback_query(F.data.startswith('category'))
async def get_subcatalog_handler(callback: CallbackQuery):
    print(callback.data)
    category_id = int(callback.data.split('_')[1])
    async with get_session() as session:
        page = 1
        start = (page - 1) * PER_PAGE
        end = start + PER_PAGE
        query = select(SubCategory).where(SubCategory.category_id == category_id).slice(start, end)
        result = await session.execute(query)
        answer = result.all()
        if answer:
            subcategories_dict = {el[0].id: el[0].name for el in answer}
            await callback.message.edit_text(text='Выбери подкатегорию', reply_markup=generate_category_keyboard(subcategories_dict, subcategory=True, category_id=category_id))
            await callback.answer()
        else:
            await callback.answer(text='В категории нет товаров', show_alert=True)


@router.callback_query(F.data.startswith('subcategory'))
async def get_products_handler(callback: CallbackQuery):
    print(callback.data)
    subcategory_id = int(callback.data.split('_')[1])
    async with get_session() as session:
        page = 1
        start = (page - 1) * PER_PAGE
        end = start + PER_PAGE
        query = select(Product).where(Product.subcategory_id == subcategory_id).slice(start, end)
        result = await session.execute(query)
        answer = result.all()
        if answer:
            pass
        else:
            await callback.answer(text='В подкатегории нет товаров', show_alert=True)


@router.callback_query(F.data == 'check_subscribe')
async def check_subscribe_handler(callback: CallbackQuery):
    user_channel_status = await bot.get_chat_member(chat_id=f'@{CHANNEL_NAME}', user_id=callback.from_user.id)
    user_group_status = await bot.get_chat_member(chat_id=f'@{GROUP_NAME}', user_id=callback.from_user.id)
    if user_channel_status.status != 'left' and user_group_status.status != 'legt':
        await callback.answer(text='Спасибо за подписку!', show_alert=True)
        await callback.message.delete()
        await bot.send_message(callback.from_user.id, f'Привет, {callback.from_user.username}!', reply_markup=main_keyboard())
    else:
        await callback.answer('Ты еще не подписался на канал или не вступил в группу', show_alert=True)


@router.callback_query(F.data.startswith('page'))
async def pagination_handler(callback: CallbackQuery):
    print(callback.data)
    async with get_session() as session:
        next_page, prefix = int(callback.data.split('_')[2]), callback.data.split('_')[1]
        category_id = int(prefix[-1])
        start = (next_page - 1) * PER_PAGE
        end = start + PER_PAGE
        query = select(Category).slice(start, end) if prefix.startswith('category') else select(SubCategory).where(SubCategory.category_id == category_id).slice(start, end)
        result = await session.execute(query)
        answer = result.all()
        if answer:
            categories_dict = {el[0].id: el[0].name for el in answer}
            message_text = 'Выбери категорию' if prefix.startswith('category') else 'Выбери подкатегорию'
            flag_subcategory = bool(prefix.startswith('subcategory'))
            await callback.message.edit_text(text=message_text, reply_markup=generate_category_keyboard(categories_dict, current_page=next_page, subcategory=flag_subcategory, category_id=category_id))
            await callback.answer()
        else:
            await callback.answer('Больше ничего нет', show_alert=True)