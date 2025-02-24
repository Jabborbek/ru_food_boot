import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.inline.get_menu_keyboard import *
from loader import dp, db, bot
from messages.button_text import main_menu_btn_txt
from messages.default_markup import get_markup_default_main
from messages.funcs.get_language_func import get_language
from messages.message_text import *
from states.order import OrderState


@dp.callback_query_handler(text='main_main', state='*')
async def get_product(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    language = await get_language(types.User.get_current().id)

    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    except Exception as e:
        logging.error(e)

    await call.message.answer(
        text=main_menu_txt[language],
        reply_markup=await get_markup_default_main(btn_txt=main_menu_btn_txt,
                                                   language=language))


@dp.callback_query_handler(text='bac_main', state=OrderState.back_product)
async def get_product(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = await get_language(types.User.get_current().id)
    products = await db.select_product(category_id=int(data.get('category_id')), status=True)
    if not products:
        await call.answer(
            text=not_products_txt[language], show_alert=True
        )
    else:
        try:
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        except Exception as e:
            logging.error(e)
        await call.message.answer(
            text=products_txt[language],
            reply_markup=await get_product_markup(
                products=products,
                language=language,
            )
        )
        await OrderState.category.set()
