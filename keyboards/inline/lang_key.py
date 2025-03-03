from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

language_keyboard = InlineKeyboardMarkup(row_width=2)
language_keyboard.insert(InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="uz"))
language_keyboard.insert(InlineKeyboardButton(text="🇷🇺 Pусский", callback_data="ru"))