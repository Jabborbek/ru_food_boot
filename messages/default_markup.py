from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


async def get_markup_default_main(language, btn_txt):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    text = btn_txt[language]
    for index, btn_text in enumerate(text):
        button = KeyboardButton(text=btn_text)
        markup.insert(button)
    return markup


def sync_get_markup_default_main(language, btn_txt):
    markup = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    text = btn_txt[language]
    for index, btn_text in enumerate(text):
        button = KeyboardButton(text=btn_text)
        if index in [1, 5]:
            markup.add(button)
        else:
            markup.insert(button)
    return markup


async def get_markup_default(language, btn_txt):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    text = btn_txt[language]
    for index, btn_text in enumerate(text):
        button = KeyboardButton(text=btn_text)
        markup.insert(button)
    return markup


async def get_markup_default_phone(language, btn_txt):
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    text = btn_txt[language]
    for btn_text in text:
        button = KeyboardButton(text=btn_text, request_contact=True)
        markup.insert(button)
    return markup


async def get_markup_default_phone_cancel(language, btn_txt):
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    text = btn_txt[language]
    for key, value in enumerate(text):
        if key == 0:
            button = KeyboardButton(text=value, request_contact=True)
            markup.insert(button)
        else:
            button = KeyboardButton(text=value)
            markup.insert(button)
    return markup


async def get_markup_inline(language, btn_txt, user_id, call_text):
    markup = InlineKeyboardMarkup(row_width=2)
    text = btn_txt[language]
    for index, btn_text in enumerate(text):
        button = InlineKeyboardButton(text=btn_text, callback_data=f'{call_text}_{user_id}')
        markup.insert(button)
    return markup


async def get_markup_inline_feedback(language, btn_txt, user_id):
    markup = InlineKeyboardMarkup(row_width=2)
    text = btn_txt[language]
    for index, btn_text in enumerate(text):
        if index == 0:
            button = InlineKeyboardButton(text=btn_text, callback_data=f'pending_{user_id}')
            markup.add(button)
        else:
            button = InlineKeyboardButton(text=btn_text, callback_data=f'cancel_feedback_{user_id}')
            markup.insert(button)
    return markup


async def get_markup_default_location_cancel(language, btn_txt):
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    text = btn_txt[language]
    for key, value in enumerate(text):
        if key == 0:
            button = KeyboardButton(text=value, request_location=True)
            markup.insert(button)
        else:
            button = KeyboardButton(text=value)
            markup.insert(button)
    return markup


async def get_markup_inline_pay_button(language, btn_txt, url):
    markup = InlineKeyboardMarkup(row_width=1)
    text = btn_txt[language]
    for index, btn_text in enumerate(text):
        button = InlineKeyboardButton(text=btn_text, url=url)

        markup.insert(button)
    return markup
