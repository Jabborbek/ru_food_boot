import datetime
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from keyboards.inline.lan_key import language_keyboard
from loader import dp, db, bot
from messages.button_text import *
from messages.default_markup import *
from messages.funcs.check_user import check_user
from messages.funcs.get_language_func import get_language
from messages.message_text import *


@dp.message_handler(CommandStart(), chat_type='private', state='*')
async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()
    if await check_user(user_id=message.from_user.id):
        language = await get_language(user_id=message.from_user.id)
        if language is None:
            await message.answer(
                text=welcome_txt,
                reply_markup=language_keyboard
            )
        else:
            await message.answer(main_menu_txt[language],
                                 reply_markup=await get_markup_default_main(btn_txt=main_menu_btn_txt,
                                                                            language=language))

    else:
        await db.add_user(telegram=str(message.from_user.id),
                          lang=None,
                          updated_at=datetime.datetime.now(),
                          created_at=datetime.datetime.now())

        await message.answer(
            text=welcome_txt,
            reply_markup=language_keyboard
        )


@dp.callback_query_handler(lambda call: call.data == "ru" or call.data == "uz")
async def language_query_handler(callback_query: types.CallbackQuery):
    try:
        await bot.delete_message(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id
        )
    except Exception as e:
        logging.error(e)
    try:
        await db.update_user_language(lang=callback_query.data, telegram=str(callback_query.from_user.id))
    except Exception as e:
        logging.error(e)
    await callback_query.message.answer(main_menu_txt[callback_query.data],
                                        reply_markup=await get_markup_default_main(btn_txt=main_menu_btn_txt,
                                                                                   language=callback_query.data))
