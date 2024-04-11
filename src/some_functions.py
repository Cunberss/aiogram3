from src.db.functions import db_get_data_products
from src.db.models import Product


def generation_message_product(product: Product) -> str:
    return f'Название: {product.name}\n\nОписание: {product.description}\n\nЦена: {product.price}р.'


def generation_message_cartitems(lst_items) -> str:
    text = 'В вашей корзине ⬇️\n\n'
    for el in lst_items:
        temp_string = f'- {el[0].capitalize()}, кол-во: {el[1]}, стоимость: {el[2]}р\n'
        text += temp_string
    text += f'\nК оплате: {sum([el[2] for el in lst_items])}р'
    return text


async def generation_order_data(products, order_id) -> str:
    list_products = [el.split(',') for el in products.split('\n')]
    list_products = [[el_1.split(':')[1], el_2.split(':')[1]] for [el_1, el_2] in list_products]
    products_ids = [int(el[0]) for el in list_products]
    quantity_list = [int(el[1]) for el in list_products]

    answer = await db_get_data_products(products_ids)

    text = f'Информация по заказу №{order_id} 👇\n\n'
    for el_1, el_2 in zip(answer, quantity_list):
        text += f'{el_1[0]}, кол-во: {el_2}, стоимость: {el_1[1]}\n'
    return text