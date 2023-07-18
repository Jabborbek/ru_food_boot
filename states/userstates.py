from aiogram.dispatcher.filters.state import StatesGroup, State


class RegState(StatesGroup):
    fullname = State()
    phone = State()
    send_code = State()


class Settings(StatesGroup):
    open = State()
    lang = State()
    fullname = State()
    phone = State()
    send_code = State()


class AddressState(StatesGroup):
    my_address = State()
    all_address = State()
    new_address = State()
    del_address = State()
    confirm = State()


class Feedback(StatesGroup):
    step = State()


class AdminFeedback(StatesGroup):
    answer = State()
