from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from messages.button_text import back_btn_txt


async def get_category_markup(categories: list, language: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    for cat in categories:
        markup.insert(InlineKeyboardButton(text=cat[f'name_{language}'], callback_data=str(cat['id'])))
    markup.add(InlineKeyboardButton(text=back_btn_txt[language], callback_data='cat_back'))
    return markup


async def get_subcategory_markup(subcategories: list) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    for subcat in subcategories:
        markup.insert(InlineKeyboardButton(text=subcat['name'], callback_data=str(subcat['id'])))
    markup.add(InlineKeyboardButton(text='🔙 Назад', callback_data='sub_cat_back'))
    markup.add(InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_main'))
    return markup


async def get_product_markup(products: list, language: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    for pro in products:
        markup.insert(InlineKeyboardButton(text=pro[f'name_{language}'], callback_data=str(pro['id'])))
    markup.add(InlineKeyboardButton(text=back_btn_txt[language], callback_data='cat_back'))
    return markup


async def _markup(button, lang) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    markup.insert(InlineKeyboardButton(text=button[lang][0], callback_data='bac_main'))
    markup.insert(InlineKeyboardButton(text=button[lang][1], callback_data='main_main'))
    return markup
