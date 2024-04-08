from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile
from sqlalchemy import select, insert, desc, delete, and_, update

from src.bot import bot
from src.config import CHANNEL_NAME, GROUP_NAME, PER_PAGE
from src.db.models import Cart, Category, SubCategory, Product, CartItem, User, Order
from src.db.base import get_session
from src.fsm import WatchProducts, OrderCreate
from src.keyboards import main_keyboard, generate_category_keyboard, product_keyboard, choose_quantity_keyboard, \
    cart_changer_keyboard, cart_keyboard, send_phone_keyboard, delete_keyboard
from src.some_functions import generation_message_product, generation_message_cartitems

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
            cart_id = int(result.all()[0][0].id)
            query = select(CartItem).where(CartItem.cart_id == cart_id)
            result = await session.execute(query)
            answer = result.all()
            if len(answer) > 9:
                await callback.answer('У вас уже полная корзина. Оформите заказ или удалите лишние товары', show_alert=True)
            else:
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

            query = select(CartItem).where(and_(CartItem.cart_id == cart_id, CartItem.product_id == product_id))
            result = await session.execute(query)
            answer = result.all()
            if not answer:
                query = insert(CartItem).values(cart_id=cart_id, product_id=product_id, quantity=quantity)
            else:
                query = update(CartItem).where(and_(CartItem.cart_id == cart_id, CartItem.product_id == product_id)).values({CartItem.quantity: CartItem.quantity + quantity})
            await session.execute(query)
            await session.commit()
        caption = callback.message.caption.replace('\n\nВыберите количество 👇', '')
        await callback.message.edit_caption(caption=caption, reply_markup=product_keyboard())
        await callback.answer(text='Товар добавлен в корзину', show_alert=True)
    else:
        await callback.answer()


@router.callback_query(StateFilter(None), F.data.startswith('cart'))
async def actions_cartitems(callback: CallbackQuery, state: FSMContext):
    response = callback.data.split('_')[1]
    if response == 'success':
        await callback.answer()
        await callback.message.delete()
        async with get_session() as session:
            query = select(User.phone).where(User.user_id == callback.from_user.id)
            result = await session.execute(query)
            answer = result.all()
            phone = answer[0][0]
            if phone == 'Unknown':
                await bot.send_message(callback.from_user.id, 'Для оформления заказа необходимо поделиться номером телефона 👇', reply_markup=send_phone_keyboard())
                await state.set_state(OrderCreate.phone)
            else:
                await bot.send_message(callback.from_user.id, 'Введите адрес доставки 👇')
                await state.set_state(OrderCreate.address)
                await state.update_data(phone=phone)

    elif response == 'change':
        async with get_session() as session:
            query = select(Cart).where(Cart.user_id == callback.from_user.id)
            result = await session.execute(query)
            answer = result.all()
            if answer:
                cart_id = answer[0][0].id
                query = select(Product.id, Product.name).join(CartItem, Product.id == CartItem.product_id).filter(
                    CartItem.cart_id == cart_id).order_by(desc(CartItem.id))
                result = await session.execute(query)
                answer = result.all()
                if answer:
                    lst_items = [el for el in answer]
                    mes = '\n\nКакой товар убрать из корзины? 👇'
                    text = callback.message.text + mes
                    await callback.message.edit_text(text=text, reply_markup=cart_changer_keyboard(lst_items, cart_id))
                else:
                    await callback.answer('Что-то пошло не так', show_alert=True)
            else:
                await callback.answer('Что-то пошло не так', show_alert=True)
    elif response == 'alldel':
        cart_id = int(callback.data.split('_')[-1])
        async with get_session() as session:
            query = delete(CartItem).where(CartItem.cart_id == cart_id)
            await session.execute(query)
            await session.commit()
            await callback.answer('Ваша корзина полностью очищена', show_alert=True)
            await callback.message.delete()
    elif response == 'back':
        text = callback.message.text.replace('\n\nКакой товар убрать из корзины? 👇', '')
        await callback.message.edit_text(text=text, reply_markup=cart_keyboard())
        await callback.answer()
    elif response == 'delete':
        product_id = int(callback.data.split('_')[-2])
        cart_id = int(callback.data.split('_')[-1])
        async with get_session() as session:
            query = delete(CartItem).where(and_(CartItem.cart_id == cart_id, CartItem.product_id == product_id))
            await session.execute(query)
            await session.commit()
            await callback.answer('Товар удален из корзины', show_alert=True)
            query = select(Product.name, CartItem.quantity,
                           (Product.price * CartItem.quantity).label('total_price')).join(CartItem,
                                                                                          Product.id == CartItem.product_id).filter(
                CartItem.cart_id == cart_id).order_by(desc(CartItem.id))
            result = await session.execute(query)
            answer = result.all()
            if answer:
                lst_items = [el for el in answer]
                mes = generation_message_cartitems(lst_items)
                await callback.message.edit_text(text=mes, reply_markup=cart_keyboard())
            else:
                await callback.answer('Ваша корзина пуста', show_alert=True)
                await callback.message.delete()


@router.callback_query(F.data.startswith('checkorder'))
async def check_order_handler(callback: CallbackQuery):
    order_id = int(callback.data.split('_')[1])
    async with get_session() as session:
        query = select(Order.products).where(Order.id == order_id)
        result = await session.execute(query)
        answer = result.all()[0][0]
        list_products = [el.split(',') for el in answer.split('\n')]
        list_products = [[el_1.split(':')[1], el_2.split(':')[1]] for [el_1, el_2] in list_products]
        products_ids = [int(el[0]) for el in list_products]
        quantity_list = [int(el[1]) for el in list_products]
        query = select(Product.name, Product.price).filter(Product.id.in_(products_ids))
        result = await session.execute(query)
        answer = [el for el in result.all()]
        text = f'Информация по заказу №{order_id} 👇\n\n'
        for el_1, el_2 in zip(answer, quantity_list):
            text += f'{el_1[0]}, кол-во: {el_2}, стоимость: {el_1[1]}\n'
        await callback.answer()
        await bot.send_message(callback.from_user.id, text=text, reply_markup=delete_keyboard())


@router.callback_query(F.data == 'delete_message')
async def delete_message_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()


@router.callback_query(F.data == 'return_to_category')
async def return_to_category_handler(callback: CallbackQuery, state: FSMContext):
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
            try:
                await callback.message.edit_text(text='Выбери категорию',
                                 reply_markup=generate_category_keyboard(categories_dict, current_page=page))
                await callback.answer()
            except Exception:
                await bot.send_message(callback.from_user.id, text='Выбери категорию',
                                 reply_markup=generate_category_keyboard(categories_dict, current_page=page))
                await callback.answer()
                await callback.message.delete()
        else:
            await callback.answer('Что-то пошло не так', show_alert=True)






