import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from asyncpg import UniqueViolationError

from keyboards.inline.lang_key import language_keyboard
from loader import dp, db, bot
from messages.button_text import *
from messages.funcs.check_user import check_user
from messages.funcs.get_language import get_language
from messages.funcs.get_markup_default import get_markup_default_main, get_markup_default_phone
from messages.funcs.send_sms_code import send_sms_code
from messages.message_text import *
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
                sms = await db.select_user_sms_code(user_id=int(user['id']))
                if sms['status']:
                    await message.answer(main_menu_txt[language],
                                         reply_markup=await get_markup_default_main(btn_txt=main_menu_btn_txt,
                                                                                    language=language))
                else:
                    await message.answer(get_phone_txt[language],
                                         reply_markup=await get_markup_default_phone(language, phone_btn_txt))
                    await RegState.phone.set()
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
                await send_sms_code(phone=message.contact.phone_number[1:13], lang=language,
                                    user_id=int(user['id']),
                                    telegram=message.from_user.id)
                await message.answer(send_smm_code_txt[language], reply_markup=types.ReplyKeyboardRemove())
                await db.update_sms_phone(phone=int(message.contact.phone_number[1:13]), user_id=int(user['id']))
                await state.update_data(phone=message.contact.phone_number[1:13])
                await RegState.send_code.set()
        else:
            all_users = await db.select_user_all()
            for u in all_users:
                if u['phone'] is not None:
                    if int(message.contact.phone_number[0:12]) == int(u['phone']):
                        await message.answer(get_phone_error_txt[language])
                        await RegState.phone.set()
                        break
            else:
                await send_sms_code(phone=message.contact.phone_number[0:12], lang=language,
                                    user_id=int(user['id']),
                                    telegram=message.from_user.id)
                await db.update_sms_phone(phone=int(message.contact.phone_number[0:12]), user_id=int(user['id']))
                await message.answer(send_smm_code_txt[language], reply_markup=types.ReplyKeyboardRemove())
                await state.update_data(phone=message.contact.phone_number[0:12])
                await RegState.send_code.set()

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
                await send_sms_code(phone=message.text[1:13], lang=language, user_id=int(user['id']),
                                    telegram=message.from_user.id)
                await message.answer(send_smm_code_txt[language], reply_markup=types.ReplyKeyboardRemove())
                await db.update_sms_phone(phone=int(message.text[1:13]), user_id=int(user['id']))
                await state.update_data(phone=message.text[1:13])
                await RegState.send_code.set()
    else:
        await message.answer(get_phone_txt[language],
                             reply_markup=await get_markup_default_phone(language, phone_btn_txt))
        await RegState.phone.set()


@dp.message_handler(content_types=['text'], state=RegState.send_code)
async def get_phone(message: types.Message, state: FSMContext):
    user = await db.select_user(telegram=message.from_user.id)
    code = await db.select_user_sms_code(user_id=int(user['id']))
    language = await get_language(user_id=message.from_user.id)
    data = await state.get_data()
    if message.text.isdigit():
        if int(message.text) == int(code['code']):
            try:
                await db.update_user_phone(phone=int(data['phone']), telegram=message.from_user.id)
            except UniqueViolationError:
                await message.answer(get_phone_error_txt[language])
                await RegState.phone.set()
                return
            await db.update_sms_status(status=True, user_id=int(user['id']))
            await message.answer(main_menu_txt[language], reply_markup=await get_markup_default_main(language=language,
                                                                                                     btn_txt=main_menu_btn_txt))
            await state.finish()
        else:
            await message.answer(send_smm_code_error_txt[language])
            await RegState.send_code.set()
    else:
        await message.answer(send_smm_code_error_notnumber_txt[language])
        await RegState.send_code.set()
