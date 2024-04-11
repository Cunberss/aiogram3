from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile

from src.bot import bot
from src.callback_factory import ProductCallbackFactory, CartCallbackFactory, OrderCallbackFactory
from src.config import CHANNEL_NAME, GROUP_NAME
from src.db.functions import db_get_subcategories, db_get_products, db_get_categories, db_get_cart, \
    db_get_cartitems_count, db_add_product_in_cart, db_get_phone, db_get_products_in_cart, db_delete_cart, \
    db_delete_product_in_cart, db_get_cartitems, db_get_order_products
from src.fsm import WatchProducts, OrderCreate
from src.keyboards import main_keyboard, generate_category_keyboard, product_keyboard, choose_quantity_keyboard, \
    cart_changer_keyboard, cart_keyboard, send_phone_keyboard, delete_keyboard
from src.some_functions import generation_message_product, generation_message_cartitems, generation_order_data

router = Router(name='callbacks-router')


@router.callback_query(F.data.startswith('category'))
async def get_subcatalog_handler(callback: CallbackQuery):
    category_id = int(callback.data.split('_')[1])
    answer = await db_get_subcategories(category_id)
    if answer:
        subcategories_dict = {el[0].id: el[0].name for el in answer}
        await callback.message.edit_text(text='Выбери подкатегорию', reply_markup=generate_category_keyboard(subcategories_dict, subcategory=True, category_id=category_id))
        await callback.answer()
    else:
        await callback.answer(text='В категории нет товаров', show_alert=True)


@router.callback_query(F.data.startswith('subcategory'))
async def get_products_handler(callback: CallbackQuery, state: FSMContext):
    subcategory_id = int(callback.data.split('_')[1])
    answer = await db_get_products(subcategory_id)
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


@router.callback_query(F.data == 'check_subscribe')
async def check_subscribe_handler(callback: CallbackQuery):
    user_channel_status = await bot.get_chat_member(chat_id=f'@{CHANNEL_NAME}', user_id=callback.from_user.id)
    user_group_status = await bot.get_chat_member(chat_id=f'@{GROUP_NAME}', user_id=callback.from_user.id)
    if user_channel_status.status != 'left' and user_group_status.status != 'left':
        await callback.answer(text='Спасибо за подписку!', show_alert=True)
        await callback.message.delete()
        await bot.send_message(callback.from_user.id, f'Привет, {callback.from_user.username}!', reply_markup=main_keyboard())
    else:
        await callback.answer('Ты еще не подписался на канал или не вступил в группу', show_alert=True)


@router.callback_query(F.data.startswith('page'))
async def pagination_handler(callback: CallbackQuery):
    next_page, prefix = int(callback.data.split('_')[2]), callback.data.split('_')[1]
    category_id = int(prefix[-1])
    answer = await db_get_categories(next_page) if prefix.startswith('category') else await db_get_subcategories(category_id, next_page)
    if answer:
        categories_dict = {el[0].id: el[0].name for el in answer}
        message_text = 'Выбери категорию' if prefix.startswith('category') else 'Выбери подкатегорию'
        flag_subcategory = bool(prefix.startswith('subcategory'))
        await callback.message.edit_text(text=message_text, reply_markup=generate_category_keyboard(categories_dict, current_page=next_page, subcategory=flag_subcategory, category_id=category_id))
        await callback.answer()
    else:
        await callback.answer('Больше ничего нет', show_alert=True)


@router.callback_query(WatchProducts.watcher, ProductCallbackFactory.filter())
async def action_products_handler(callback: CallbackQuery, callback_data: ProductCallbackFactory, state: FSMContext):
    if callback_data.action == 'next':
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

    elif callback_data.action == 'back':
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

    elif callback_data.action == 'incart':
        cart_id = await db_get_cart(callback.from_user.id)
        answer = await db_get_cartitems_count(cart_id)
        if len(answer) > 9:
            await callback.answer('У вас уже полная корзина. Оформите заказ или удалите лишние товары', show_alert=True)
        else:
            current_caption = callback.message.caption + '\n\nВыберите количество 👇'
            await callback.message.edit_caption(caption=current_caption, reply_markup=choose_quantity_keyboard())
            await callback.answer()

    elif callback_data.action == 'return':
        caption = callback.message.caption.replace('\n\nВыберите количество 👇', '')
        await callback.message.edit_caption(caption=caption, reply_markup=product_keyboard())
        await callback.answer()

    elif callback_data.action == 'incart+' or callback_data.action == 'incart-':
        current_quantity = callback_data.quantity
        quantity = current_quantity + 1 if callback_data.action[-1] == '+' else current_quantity - 1
        try:
            await callback.message.edit_reply_markup(reply_markup=choose_quantity_keyboard(quantity))
        except TelegramBadRequest:
            pass
        await callback.answer()

    elif callback_data.action == 'saveincart':
        quantity = callback_data.quantity
        data = await state.get_data()
        product_id = data['products'][0].id
        cart_id = await db_get_cart(callback.from_user.id)
        await db_add_product_in_cart(cart_id, product_id, quantity)

        caption = callback.message.caption.replace('\n\nВыберите количество 👇', '')
        await callback.message.edit_caption(caption=caption, reply_markup=product_keyboard())
        await callback.answer(text='Товар добавлен в корзину', show_alert=True)

    else:
        await callback.answer()


@router.callback_query(CartCallbackFactory.filter())
async def actions_cartitems(callback: CallbackQuery,callback_data: CartCallbackFactory, state: FSMContext):
    response = callback_data.action
    if response == 'success':
        await callback.answer()
        await callback.message.delete()
        phone = await db_get_phone(callback.from_user.id)
        if phone == 'Unknown':
            await bot.send_message(callback.from_user.id, 'Для оформления заказа необходимо поделиться номером телефона 👇', reply_markup=send_phone_keyboard())
            await state.set_state(OrderCreate.phone)
        else:
            await bot.send_message(callback.from_user.id, 'Введите адрес доставки 👇')
            await state.set_state(OrderCreate.address)
            await state.update_data(phone=phone)

    elif response == 'change':
        cart_id = await db_get_cart(callback.from_user.id)
        answer = await db_get_products_in_cart(cart_id)
        if answer:
            lst_items = [el for el in answer]
            mes = '\n\nКакой товар убрать из корзины? 👇'
            text = callback.message.text + mes
            await callback.message.edit_text(text=text, reply_markup=cart_changer_keyboard(lst_items, cart_id))
        else:
            await callback.answer('Что-то пошло не так', show_alert=True)

    elif response == 'alldel':
        await db_delete_cart(callback.from_user.id, callback_data.cart_id)
        await callback.answer('Ваша корзина полностью очищена', show_alert=True)
        await callback.message.delete()

    elif response == 'back':
        text = callback.message.text.replace('\n\nКакой товар убрать из корзины? 👇', '')
        await callback.message.edit_text(text=text, reply_markup=cart_keyboard())
        await callback.answer()

    elif response == 'delete':
        await db_delete_product_in_cart(callback_data.cart_id, callback_data.product_id)
        await callback.answer('Товар удален из корзины', show_alert=True)

        answer = await db_get_cartitems(callback_data.cart_id)
        if answer:
            lst_items = [el for el in answer]
            mes = generation_message_cartitems(lst_items)
            await callback.message.edit_text(text=mes, reply_markup=cart_keyboard())
        else:
            await callback.answer('Ваша корзина пуста', show_alert=True)
            await callback.message.delete()


@router.callback_query(OrderCallbackFactory.filter())
async def check_order_handler(callback: CallbackQuery, callback_data: OrderCallbackFactory):
    order_id = callback_data.order_id
    answer = await db_get_order_products(order_id)
    text = await generation_order_data(answer, order_id)
    await callback.answer()
    await bot.send_message(callback.from_user.id, text=text, reply_markup=delete_keyboard())


@router.callback_query(F.data == 'delete_message')
async def delete_message_handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()


@router.callback_query(F.data == 'return_to_category')
async def return_to_category_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    answer = await db_get_categories()
    if answer:
        categories_dict = {el[0].id: el[0].name for el in answer}
        try:
            await callback.message.edit_text(text='Выбери категорию',
                             reply_markup=generate_category_keyboard(categories_dict, current_page=1))
            await callback.answer()
        except Exception:
            await bot.send_message(callback.from_user.id, text='Выбери категорию',
                             reply_markup=generate_category_keyboard(categories_dict, current_page=1))
            await callback.answer()
            await callback.message.delete()
    else:
        await callback.answer('Что-то пошло не так', show_alert=True)






