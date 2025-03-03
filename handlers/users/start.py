import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from func_and_message.button_text import *
from func_and_message.funcs.check_user import check_user
from func_and_message.funcs.get_language import get_language
from func_and_message.funcs.get_markup_default import get_markup_default_main, get_markup_default_phone
from func_and_message.message_text import *
from keyboards.inline.lang_key import language_keyboard
from loader import dp, db, bot
from states.userstates import RegState


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
            user = await db.select_user(telegram=message.from_user.id)
            if user['fullname'] is None:
                await message.answer(get_name_txt[language])
                await RegState.fullname.set()
            elif user['phone'] is None:
                await message.answer(get_phone_txt[language],
                                     reply_markup=await get_markup_default_phone(language, phone_btn_txt))
                await RegState.phone.set()
            else:

                await message.answer(main_menu_txt[language],
                                     reply_markup=await get_markup_default_main(language=language,
                                                                                btn_txt=main_menu_btn_txt))
                await state.finish()
    else:
        await db.add_user(fullname=None,
                          lang=None,
                          telegram=message.from_user.id,
                          phone=None,
                          create_date=datetime.datetime.now())

        await message.answer(
            text=welcome_txt,
            reply_markup=language_keyboard
        )


@dp.callback_query_handler(lambda call: call.data == "ru" or call.data == "uz")
async def language_query_handler(callback_query: types.CallbackQuery):
    await bot.delete_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id
    )
    await db.update_user_language(lang=callback_query.data, telegram=callback_query.from_user.id)

    user = await db.select_user(telegram=callback_query.from_user.id)
    if user['fullname'] is None:
        await callback_query.message.answer(get_name_txt[callback_query.data])
        await RegState.fullname.set()
    else:
        await callback_query.message.answer(main_menu_txt[callback_query.data],
                                            reply_markup=await get_markup_default_main(btn_txt=main_menu_btn_txt,
                                                                                       language=callback_query.data))


@dp.message_handler(state=RegState.fullname, content_types=[types.ContentType.TEXT])
async def reg_to_bot(message: types.Message):
    language = await get_language(user_id=message.from_user.id)
    if message.text.isdigit():
        await message.answer(get_name_error_txt[language])
        await RegState.fullname.set()
    else:
        await db.update_user_fullname(fullname=message.text, telegram=message.from_user.id)
        await message.answer(get_phone_txt[language],
                             reply_markup=await get_markup_default_phone(language, phone_btn_txt))
        await RegState.phone.set()


@dp.message_handler(state=RegState.phone, content_types=[types.ContentType.CONTACT, types.ContentType.TEXT])
async def reg_to_bot(message: types.Message, state: FSMContext):
    language = await get_language(user_id=message.from_user.id)
    user = await db.select_user(telegram=message.from_user.id)
    if message.content_type == 'contact':
        if message.contact.phone_number.startswith('+'):
            all_users = await db.select_user_all()
            for u in all_users:
                if u['phone'] is not None:
                    if int(message.contact.phone_number[1:13]) == int(u['phone']):
                        await message.answer(get_phone_error_txt[language])
                        await RegState.phone.set()
                        break

            else:
                await db.update_user_phone(phone=int(message.contact.phone_number[1:13]), telegram=message.from_user.id)
                await state.update_data(phone=message.contact.phone_number[1:13])
                await message.answer(main_menu_txt[language],
                                     reply_markup=await get_markup_default_main(language=language,
                                                                                btn_txt=main_menu_btn_txt))
        else:
            all_users = await db.select_user_all()
            for u in all_users:
                if u['phone'] is not None:
                    if int(message.contact.phone_number[0:12]) == int(u['phone']):
                        await message.answer(get_phone_error_txt[language])
                        await RegState.phone.set()
                        break
            else:
                await db.update_user_phone(phone=int(message.contact.phone_number[0:12]), telegram=message.from_user.id)
                await state.update_data(phone=message.contact.phone_number[0:12])
                await message.answer(main_menu_txt[language],
                                     reply_markup=await get_markup_default_main(language=language,
                                                                                btn_txt=main_menu_btn_txt))

    elif message.content_type == 'text' and len(message.text) == 13:
        if message.text.startswith('+998'):
            all_users = await db.select_user_all()
            for u in all_users:
                if u['phone'] is not None:
                    if int(message.text[1:13]) == int(u['phone']):
                        await message.answer(get_phone_error_txt[language])
                        await RegState.phone.set()
                        break
            else:
                await db.update_user_phone(phone=int(message.text[1:13]), telegram=message.from_user.id)
                await state.update_data(phone=message.text[1:13])
                await message.answer(main_menu_txt[language],
                                     reply_markup=await get_markup_default_main(language=language,
                                                                                btn_txt=main_menu_btn_txt))
    else:
        await message.answer(get_phone_txt[language],
                             reply_markup=await get_markup_default_phone(language, phone_btn_txt))
        await RegState.phone.set()
