from aiogram.fsm.state import StatesGroup, State


class WatchProducts(StatesGroup):
    watcher = State()


class OrderCreate(StatesGroup):
    phone = State()
    address = State()