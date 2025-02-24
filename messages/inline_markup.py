from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from messages.button_text import back_btn_txt


async def get_markup_inline(language, btn_txt):
    markup = InlineKeyboardMarkup(row_width=2)
    text = btn_txt[language]
    for index, btn_text in enumerate(text):
        if index == 0:
            button = InlineKeyboardButton(text=btn_text, callback_data='yes')
            markup.insert(button)
        else:
            button = InlineKeyboardButton(text=btn_text, callback_data='no')
            markup.insert(button)
    return markup


async def get_markup_inline_delete(language, btn_txt, id_list: list = None):
    markup = InlineKeyboardMarkup(row_width=2)

    text = btn_txt[language]
    for index, value in enumerate(id_list, start=1):
        markup.insert(InlineKeyboardButton(text=str(index), callback_data=f'{value}'))

    button = InlineKeyboardButton(text=text[0], callback_data='delete')
    markup.add(button)
    markup.add(InlineKeyboardButton(text=back_btn_txt[language], callback_data='address_back'))

    return markup
