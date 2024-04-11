from typing import Optional
from aiogram.filters.callback_data import CallbackData


class ProductCallbackFactory(CallbackData, prefix="product"):
    action: str
    quantity: Optional[int] = None


class CartCallbackFactory(CallbackData, prefix="cart"):
    action: str
    product_id: Optional[int] = None
    cart_id: Optional[int] = None


class OrderCallbackFactory(CallbackData, prefix="checkorder"):
    order_id: int
