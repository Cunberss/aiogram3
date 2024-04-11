from typing import Optional
from aiogram.filters.callback_data import CallbackData


class ProductCallbackFactory(CallbackData, prefix="product"):
    action: str
    quantity: Optional[int] = None

