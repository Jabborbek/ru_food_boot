from aiogram.dispatcher.filters.state import StatesGroup, State


class OrderState(StatesGroup):
    category = State()
    product = State()
    measure = State()
    birlik = State()
    quantity = State()
    back = State()


class CartState(StatesGroup):
    main = State()
    delete = State()
    officialization = State()
    dastavka = State()
    payments = State()
    invoice = State()
