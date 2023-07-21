from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
main_menu_kb.insert(KeyboardButton(text='🛍 Продукты'))
main_menu_kb.insert(KeyboardButton(text='🛠 Поддерживать'))
