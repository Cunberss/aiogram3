from aiogram.fsm.state import StatesGroup, State


class WatchProducts(StatesGroup):
    watcher = State()