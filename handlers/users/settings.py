from loader import dp, db, bot
from aiogram import types
from aiogram.dispatcher import FSMContext

from messages.funcs.get_language import get_language
from keyboards.inline.lang_key import language_keyboard
from messages.button_text import *
from messages.funcs.send_sms_code import send_sms_code
from messages.message_text import *
from messages.funcs.get_markup_default import get_markup_default, get_markup_default_phone, get_markup_default_main, \
    get_markup_default_phone_cancel
from states.userstates import Settings


@dp.message_handler(text=["⚙️Sozlamalar", "⚙️Настройки"], state='*')
async def get_settings(message: types.Message, state: FSMContext):
    await state.finish()
    language = await get_language(types.User.get_current().id)
    await message.answer(text=settings_txt[language], reply_markup=await get_markup_default(language, settings_btn_txt))
    await Settings.open.set()


@dp.message_handler(text=["❌ Bekor qilish", "❌ Отменить"], state=[Settings.fullname, Settings.phone])
async def get_settings(message: types.Message, state: FSMContext):
    await state.finish()
    language = await get_language(types.User.get_current().id)
    await message.answer(text=cancel_txt[language], reply_markup=await get_markup_default(language, settings_btn_txt))
    await Settings.open.set()


@dp.message_handler(text=["🔄 Tilni o'zgartirish", "🔄 Изменить язык"], state=Settings.open)
async def change_lan(message: types.Message):
    language = await get_language(types.User.get_current().id)
    await message.answer(text=change_language_txt[language], reply_markup=language_keyboard)
    await Settings.lang.set()


@dp.callback_query_handler(lambda call: call.data == "ru" or call.data == "uz", state=Settings.lang)
async def language_query_handler(call: types.CallbackQuery):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await call.message.answer(success_txt[call.data],
                              reply_markup=await get_markup_default(call.data, settings_btn_txt))
    await db.update_user_language(lang=call.data, telegram=call.from_user.id)
    await Settings.open.set()


@dp.message_handler(text=["📌 FISH o'zgartirish", "📌 Изменение ФИО"], state=Settings.open)
async def change_lan(message: types.Message):
    language = await get_language(types.User.get_current().id)
    await message.answer(text=get_name_txt[language], reply_markup=await get_markup_default(language, cancel_btn_txt))
    await Settings.fullname.set()


@dp.message_handler(content_types='text', state=Settings.fullname)
async def change_lan(message: types.Message):
    language = await get_language(types.User.get_current().id)
    if not message.text.isdigit():
        await db.update_user_fullname(fullname=message.text, telegram=message.from_user.id)
        await message.answer(text=success_txt[language],
                             reply_markup=await get_markup_default(language, settings_btn_txt))
        await Settings.open.set()
    else:
        await message.answer(text=get_name_error_txt[language])
        await Settings.fullname.set()


@dp.message_handler(text=["📞 Telfon nomerni o'zgartirish", "📞 Изменить номер телефона"], state=Settings.open)
async def change_lan(message: types.Message):
    print(message.text)
    language = await get_language(types.User.get_current().id)
    await message.answer(text=get_phone_txt[language],
                         reply_markup=await get_markup_default_phone_cancel(language=language, btn_txt=phone_cancel_btn_txt))
    await Settings.phone.set()


@dp.message_handler(state=Settings.phone, content_types=[types.ContentType.CONTACT, types.ContentType.TEXT])
async def reg_to_bot(message: types.Message, state: FSMContext):
    language = await get_language(user_id=message.from_user.id)
    user = await db.select_user(telegram=message.from_user.id)
    print(message.text)
    if message.content_type == 'contact':
        if message.contact.phone_number.startswith('+'):
            all_users = await db.select_user_all()
            for u in all_users:
                if u['phone'] is not None:
                    if int(message.contact.phone_number[1:13]) == int(u['phone']):
                        await message.answer(get_phone_error_txt[language])
                        await Settings.phone.set()
                        break

            else:
                await send_sms_code(phone=message.contact.phone_number[1:13], lang=language,
                                    user_id=int(user['id']),
                                    telegram=message.from_user.id)
                await message.answer(send_smm_code_txt[language], reply_markup=types.ReplyKeyboardRemove())
                await db.update_sms_phone(phone=int(message.contact.phone_number[1:13]), user_id=int(user['id']))
                await state.update_data(phone=message.contact.phone_number[1:13])
                await Settings.send_code.set()
        else:
            print(message.text)
            all_users = await db.select_user_all()
            for u in all_users:
                if u['phone'] is not None:
                    if int(message.contact.phone_number[0:12]) == int(u['phone']):
                        await message.answer(get_phone_error_txt[language])
                        await Settings.phone.set()
                        break
            else:
                await send_sms_code(phone=message.contact.phone_number[0:12], lang=language,
                                    user_id=int(user['id']),
                                    telegram=message.from_user.id)
                await db.update_sms_phone(phone=int(message.contact.phone_number[0:12]), user_id=int(user['id']))
                await message.answer(send_smm_code_txt[language], reply_markup=types.ReplyKeyboardRemove())
                await state.update_data(phone=message.contact.phone_number[0:12])
                await Settings.send_code.set()

    elif message.content_type == 'text' and len(message.text) == 13:
        if message.text.startswith('+998'):
            all_users = await db.select_user_all()
            for u in all_users:
                if u['phone'] is not None:
                    if int(message.text[1:13]) == int(u['phone']):
                        await message.answer(get_phone_error_txt[language])
                        await Settings.phone.set()
                        break
            else:
                await send_sms_code(phone=message.text[1:13], lang=language, user_id=int(user['id']),
                                    telegram=message.from_user.id)
                await message.answer(send_smm_code_txt[language], reply_markup=types.ReplyKeyboardRemove())
                await db.update_sms_phone(phone=int(message.text[1:13]), user_id=int(user['id']))
                await state.update_data(phone=message.text[1:13])
                await Settings.send_code.set()
    else:
        await message.answer(get_phone_txt[language],
                             reply_markup=await get_markup_default_phone_cancel(language, phone_cancel_btn_txt))
        await Settings.phone.set()


@dp.message_handler(content_types=['text'], state=Settings.send_code)
async def get_phone(message: types.Message, state: FSMContext):
    user = await db.select_user(telegram=message.from_user.id)
    code = await db.select_user_sms_code(user_id=int(user['id']))
    language = await get_language(user_id=message.from_user.id)
    data = await state.get_data()
    if message.text.isdigit():
        if int(message.text) == int(code['code']):
            await db.update_user_phone(phone=int(data['phone']), telegram=message.from_user.id)
            await db.update_sms_status(status=True, user_id=int(user['id']))
            await message.answer(success_txt[language], reply_markup=await get_markup_default(language=language,
                                                                                              btn_txt=settings_btn_txt))
            await Settings.open.set()
        else:
            await message.answer(send_smm_code_error_txt[language])
            await Settings.send_code.set()
    else:
        await message.answer(send_smm_code_error_notnumber_txt[language])
        await Settings.send_code.set()


@dp.message_handler(text=["🏠 Asosiy sahifa", "🏠 Главная страница"], state=Settings.open)
async def change_lan(message: types.Message, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    await message.answer(main_menu_txt[language], reply_markup=await get_markup_default_main(language=language,
                                                                                             btn_txt=main_menu_btn_txt))
    await state.finish()
