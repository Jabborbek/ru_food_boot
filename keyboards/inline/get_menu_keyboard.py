from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def get_category_markup(categories: list) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    for cat in categories:
        markup.insert(InlineKeyboardButton(text=cat['name'], callback_data=str(cat['id'])))
    markup.add(InlineKeyboardButton(text='🔙 Назад', callback_data='cat_back'))
    return markup


async def get_subcategory_markup(subcategories: list) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    for subcat in subcategories:
        markup.insert(InlineKeyboardButton(text=subcat['name'], callback_data=str(subcat['id'])))
    markup.add(InlineKeyboardButton(text='🔙 Назад', callback_data='sub_cat_back'))
    markup.add(InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_main'))
    return markup


async def get_product_markup(products: list) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    for product in products:
        markup.insert(InlineKeyboardButton(text=product['name'], callback_data=str(product['id'])))
    markup.add(InlineKeyboardButton(text='🔙 Назад', callback_data='product_back'))
    markup.add(InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_main'))
    return markup


async def _markup() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    markup.insert(InlineKeyboardButton(text='🔙 Назад', callback_data='bac_main'))
    markup.insert(InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_main'))
    return markup
