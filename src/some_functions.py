from src.db.models import Product


def generation_message_product(product: Product):
    return f'Название: {product.name}\n\nОписание: {product.description}\n\nЦена: {product.price}р.'
