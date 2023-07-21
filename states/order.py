from aiogram.dispatcher.filters.state import StatesGroup, State


class OrderState(StatesGroup):
    category = State()
    subcategory = State()
    product = State()
    back_product = State()
