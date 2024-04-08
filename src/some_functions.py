from src.db.models import Product, CartItem


def generation_message_product(product: Product) -> str:
    return f'Название: {product.name}\n\nОписание: {product.description}\n\nЦена: {product.price}р.'


def generation_message_cartitems(lst_items) -> str:
    text = 'В вашей корзине ⬇️\n\n'
    for el in lst_items:
        temp_string = f'- {el[0].capitalize()}, кол-во: {el[1]}, стоимость: {el[2]}р\n'
        text += temp_string
    text += f'\nК оплате: {sum([el[2] for el in lst_items])}р'
    return text