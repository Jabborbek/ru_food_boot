import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.inline.get_menu_keyboard import _markup
from loader import dp, db, bot
from messages.button_text import back_and_main_btn_txt
from messages.funcs.get_language_func import get_language
from messages.message_text import *
from states.order import OrderState


@dp.callback_query_handler(state=OrderState.product)
async def get_product(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(types.User.get_current().id)

    product = await db.select_product_single(id=int(call.data))
    if not product:
        await call.answer(
            text=not_products_txt[language], show_alert=True
        )
    else:
        try:
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        except Exception as e:
            logging.error(e)

        await bot.send_photo(
            chat_id=call.from_user.id,
            photo=types.InputFile(path_or_bytesio=f"media/{product['image']}"),
            caption=order_product_txt[language].format(product[f'name_{language}'], str(product['price']).split('.')[0],
                                                       product['description']),
            reply_markup=await _markup(lang=language, button=back_and_main_btn_txt)
        )

        await OrderState.back_product.set()
