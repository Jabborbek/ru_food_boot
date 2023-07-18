from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardButton, InlineKeyboardMarkup

from messages.button_text import back_btn_txt, cart_btn_txt, delete_adress_btn_txt


async def get_category_markup(categories: list, language: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    for cat in categories:
        markup.insert(InlineKeyboardButton(text=cat[f'name_{language}'], callback_data=str(cat['id'])))
    markup.add(InlineKeyboardButton(text=back_btn_txt[language], callback_data='cat_back'))
    return markup


async def get_product_markup(products: list, language: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    for pro in products:
        markup.insert(InlineKeyboardButton(text=pro[f'name_{language}'], callback_data=str(pro['id'])))
    markup.add(InlineKeyboardButton(text=back_btn_txt[language], callback_data='cat_back'))
    return markup


async def get_order_markup(args: list, language: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    for arg in args:
        markup.insert(InlineKeyboardButton(text=arg, callback_data=arg))
    markup.add(InlineKeyboardButton(text=back_btn_txt[language], callback_data='order_back'))
    return markup


async def get_measure_markup(args: str, language: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=3)
    markup.insert(InlineKeyboardButton(text="➖", callback_data='-'))
    markup.insert(InlineKeyboardButton(text=args, callback_data='nullable'))
    markup.insert(InlineKeyboardButton(text="➕", callback_data='+'))
    markup.add(InlineKeyboardButton(text=cart_btn_txt[language], callback_data='add_cart'))
    markup.add(InlineKeyboardButton(text=back_btn_txt[language], callback_data='cat_back'))
    return markup


async def get_cart_markup(args: list, language: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)
    for arg in args:
        markup.insert(InlineKeyboardButton(text=arg, callback_data=arg))
    return markup


async def get_cart_markup_2(args: list, language: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    for arg in args:
        markup.insert(InlineKeyboardButton(text=arg, callback_data=arg))
    return markup


async def get_cart_delete_markup(args: dict, language: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=4)
    for key, value in args.items():
        markup.insert(InlineKeyboardButton(text="➖", callback_data=f"-{value} {key.split(' ')[1]}_{key.split(' ')[0]}"))
        markup.insert(InlineKeyboardButton(text=f"{value} {key.split(' ')[1]}", callback_data=f"{key}_{value}_{value}"))
        markup.insert(InlineKeyboardButton(text="➕", callback_data=f"+{value} {key.split(' ')[1]}_{key.split(' ')[0]}"))
        markup.insert(InlineKeyboardButton(text="🗑", callback_data=f"del_{value}_{key.split(' ')[0]}"))

    markup.add(InlineKeyboardButton(text=delete_adress_btn_txt[language][0], callback_data='delete_all_cart'))
    markup.add(InlineKeyboardButton(text=back_btn_txt[language], callback_data='cart_back'))
    return markup


async def get_dastavka_markup(args: dict, language: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    for key, value in args.items():
        markup.insert(InlineKeyboardButton(text=str(value), callback_data=str(key)))
    markup.add(InlineKeyboardButton(text=back_btn_txt[language], callback_data='das_back'))
    return markup


async def get_payments_markup(args: list, language: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    for arg in args:
        markup.insert(InlineKeyboardButton(text=arg, callback_data=arg))
    markup.add(InlineKeyboardButton(text=back_btn_txt[language], callback_data='pay_back'))
    return markup


async def get_order_admin_markup(args: list, user_id: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)
    for arg in args:
        markup.insert(InlineKeyboardButton(text=arg, callback_data=f"{arg}_{user_id}"))
    return markup
