from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from sqlalchemy import select, insert

from src.bot import bot
from src.config import CHANNEL_NAME, GROUP_NAME, PER_PAGE
from src.db.models import User, Cart, Category, SubCategory, Product, CartItem
from src.db.base import get_session
from src.fsm import WatchProducts
from src.keyboards import main_keyboard, generate_category_keyboard, product_keyboard, choose_quantity_keyboard
from src.some_functions import generation_message_product

router = Router(name='callbacks-router')


@router.callback_query(StateFilter(None), F.data.startswith('category'))
async def get_subcatalog_handler(callback: CallbackQuery):
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


@router.callback_query(StateFilter(None), F.data.startswith('subcategory'))
async def get_products_handler(callback: CallbackQuery, state: FSMContext):
    subcategory_id = int(callback.data.split('_')[1])
    async with get_session() as session:
        query = select(Product).where(Product.subcategory_id == subcategory_id)
        result = await session.execute(query)
        answer = result.all()
        if answer:
            list_products = [el[0] for el in answer]
            await state.set_state(WatchProducts.watcher)
            await state.update_data(products=list_products, back_products=list_products)
            image = FSInputFile(list_products[0].photo_url)
            await bot.send_photo(callback.from_user.id, image, caption=generation_message_product(list_products[0]), reply_markup=product_keyboard())
            await callback.answer()
            await callback.message.delete()
        else:
            await callback.answer(text='В подкатегории нет товаров', show_alert=True)


@router.callback_query(StateFilter(None), F.data == 'check_subscribe')
async def check_subscribe_handler(callback: CallbackQuery):
    user_channel_status = await bot.get_chat_member(chat_id=f'@{CHANNEL_NAME}', user_id=callback.from_user.id)
    user_group_status = await bot.get_chat_member(chat_id=f'@{GROUP_NAME}', user_id=callback.from_user.id)
    if user_channel_status.status != 'left' and user_group_status.status != 'legt':
        await callback.answer(text='Спасибо за подписку!', show_alert=True)
        await callback.message.delete()
        await bot.send_message(callback.from_user.id, f'Привет, {callback.from_user.username}!', reply_markup=main_keyboard())
    else:
        await callback.answer('Ты еще не подписался на канал или не вступил в группу', show_alert=True)


@router.callback_query(StateFilter(None), F.data.startswith('page'))
async def pagination_handler(callback: CallbackQuery):
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


@router.callback_query(WatchProducts.watcher, F.data.startswith('product'))
async def action_products_handler(callback: CallbackQuery, state: FSMContext):
    response = callback.data.split('_')[1]
    if response == 'next':
        data = await state.get_data()
        list_products = data['products']
        if len(list_products) > 1:
            list_products = list_products[1:]
            await state.update_data(products=list_products)
            image = FSInputFile(list_products[0].photo_url)
            await bot.send_photo(callback.from_user.id, image, caption=generation_message_product(list_products[0]),
                                 reply_markup=product_keyboard())
            await callback.answer()
            await callback.message.delete()
        else:
            await callback.answer('Это последний товар', show_alert=True)
    elif response == 'back':
        data = await state.get_data()
        list_products = data['products']
        index_current_product = data['back_products'].index(list_products[0])
        if index_current_product > 0:
            list_products = [data['back_products'][index_current_product-1], *data['products']]
            await state.update_data(products=list_products)
        else:
            await callback.answer('Это первый товар', show_alert=True)
            return
        if list_products:
            image = FSInputFile(list_products[0].photo_url)
            await bot.send_photo(callback.from_user.id, image, caption=generation_message_product(list_products[0]),
                                 reply_markup=product_keyboard())
            await callback.answer()
            await callback.message.delete()
    elif response == 'incart':
        current_caption = callback.message.caption
        current_caption += '\n\nВыберите количество 👇'
        await callback.message.edit_caption(caption=current_caption, reply_markup=choose_quantity_keyboard())
        await callback.answer()
    elif response == 'return':
        caption = callback.message.caption.replace('\n\nВыберите количество 👇', '')
        await callback.message.edit_caption(caption=caption, reply_markup=product_keyboard())
        await callback.answer()
    elif response == 'incart+' or response == 'incart-':
        current_quantity = int(callback.data.split('_')[-1])
        quantity = current_quantity + 1 if response[-1] == '+' else current_quantity - 1
        try:
            await callback.message.edit_reply_markup(reply_markup=choose_quantity_keyboard(quantity))
        except TelegramBadRequest:
            pass
        await callback.answer()
    elif response == 'saveincart':
        quantity = int(callback.data.split('_')[-1])
        data = await state.get_data()
        product_id = data['products'][0].id
        async with get_session() as session:
            query = select(Cart).where(Cart.user_id == callback.from_user.id)
            result = await session.execute(query)
            answer = result.all()
            if not answer:
                query = insert(Cart).values(user_id=callback.from_user.id)
            await session.execute(query)
            await session.commit()
            query = select(Cart).where(Cart.user_id == callback.from_user.id)
            result = await session.execute(query)
            cart_id = result.all()[0][0].id
            query = insert(CartItem).values(cart_id=cart_id, product_id=product_id, quantity=quantity)
            await session.execute(query)
            await session.commit()
        caption = callback.message.caption.replace('\n\nВыберите количество 👇', '')
        await callback.message.edit_caption(caption=caption, reply_markup=product_keyboard())
        await callback.answer(text='Товар добавлен в корзину', show_alert=True)
    else:
        await callback.answer()


