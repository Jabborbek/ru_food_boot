import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.default.main_kb import main_menu_kb
from keyboards.inline.get_menu_keyboard import *
from loader import dp, db, bot
from messages.button_text import main_menu_btn_txt
from messages.default_markup import get_markup_default_main
from messages.funcs.get_language_func import get_language
from messages.message_text import *
from states.order import OrderState


@dp.message_handler(text=["🛍 Mahsulotlar", '🛍 Продукты'], state='*')
async def get_category(message: types.Message, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    categories = await db.select_category()
    if not categories:
        await message.answer(category_empty_txt[language])
    else:
        await message.answer(category_txt[language], reply_markup=types.ReplyKeyboardRemove())
        await message.answer(text=category_menu_txt[language],
                             reply_markup=await get_category_markup(categories=categories, language=language))

        await OrderState.category.set()


@dp.callback_query_handler(text='cat_back', state=OrderState.category)
async def get_category(call: types.CallbackQuery, state: FSMContext):
    print('Daa')
    language = await get_language(types.User.get_current().id)
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    except Exception as e:
        logging.error("Delete message: ", e)
    await call.message.answer(main_menu_txt[language],
                              reply_markup=await get_markup_default_main(btn_txt=main_menu_btn_txt,
                                                                         language=language))
    await state.finish()


@dp.callback_query_handler(state=OrderState.category)
async def get_category(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    products = await db.select_product(category_id=int(call.data), status=True)
    if not products:
        await call.answer(not_products_txt[language], show_alert=True)
    else:
        try:
            await call.message.edit_text(text=products_txt[language],
                                         reply_markup=await get_product_markup(products=products, language=language))
            await state.update_data(category_id=call.data)
            await OrderState.product.set()
        except Exception as e:
            logging.error("Edit message: ", e)
            # await call.message.answer(main_menu_txt[language],
            #                           reply_markup=await get_markup_default_main(btn_txt=main_menu_btn_txt,
            #                                                                      language=language))
            # await state.finish()
