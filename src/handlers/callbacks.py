from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, insert
from src.db.models import User, Cart, Category, SubCategory
from src.db.base import get_session
from src.keyboards import main_keyboard, generate_category_keyboard

router = Router(name='callbacks-router')


@router.callback_query(F.data.startswith('category'))
async def subcatalog_handler(callback: CallbackQuery):
    category_id = int(callback.data.split('_')[1])
    async with get_session() as session:
        query = select(SubCategory).where(SubCategory.category_id == category_id)
        result = await session.execute(query)
        answer = result.all()
        if answer:
            subcategories_dict = {el[0].id: el[0].name for el in answer}
            await callback.message.edit_text(text='Выбери подкатегорию', reply_markup=generate_category_keyboard(subcategories_dict, subcategory=True))
            await callback.answer()
        else:
            await callback.answer(text='В категории нет товаров', show_alert=True)
