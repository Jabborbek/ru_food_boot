from aiogram import types
from aiogram.dispatcher import FSMContext
from geopy.geocoders import Nominatim

from loader import dp, bot, db
from func_and_message.button_text import *
from func_and_message.funcs.get_language import get_language
from func_and_message.funcs.get_markup_default import get_markup_default, get_markup_default_main, \
    get_markup_default_location_cancel
from func_and_message.funcs.get_markup_inline import get_markup_inline, get_markup_inline_delete
from func_and_message.message_text import *
from states.userstates import AddressState


@dp.message_handler(text=["📍Manzillarim", "📍Мои адреса"], state='*')
async def get_address(message: types.Message):
    language = await get_language(user_id=message.from_user.id)
    await message.answer(my_address_txt[language],
                         reply_markup=await get_markup_default(language=language, btn_txt=my_address_btn_txt))
    await AddressState.my_address.set()


@dp.message_handler(text=["➕ Yangi manzil qo'shish", "➕ Добавить новый адрес"], state=AddressState.my_address)
async def get_address(message: types.Message):
    language = await get_language(user_id=message.from_user.id)
    await message.answer(my_new_address_txt[language],
                         reply_markup=await get_markup_default_location_cancel(language=language,
                                                                               btn_txt=location_btn_txt))
    await AddressState.new_address.set()


@dp.message_handler(text=["🔙 Orqaga", "🔙 Назад"], state=AddressState.new_address)
async def get_settings(message: types.Message):
    language = await get_language(types.User.get_current().id)
    await message.answer(my_address_txt[language],
                         reply_markup=await get_markup_default(language=language, btn_txt=my_address_btn_txt))
    await AddressState.my_address.set()


@dp.message_handler(text=["🔙 Orqaga", "🔙 Назад"], state=AddressState.my_address)
async def get_settings(message: types.Message, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    await message.answer(main_menu_txt[language],
                         reply_markup=await get_markup_default_main(btn_txt=main_menu_btn_txt,
                                                                    language=language))
    await state.finish()


@dp.message_handler(content_types=types.ContentType.LOCATION, state=AddressState.new_address)
async def get_address(message: types.Message, state: FSMContext):
    language = await get_language(user_id=message.from_user.id)
    user = await db.select_user(telegram=message.from_user.id)
    address = await db.select_address_(latitude=message.location.latitude,
                                       longitude=message.location.longitude,
                                       user_id=user['id'])
    if address is not None:
        await message.answer(address_always_have_txt[language])
        await AddressState.new_address.set()
    else:

        await state.update_data(latitude=message.location.latitude,
                                longitude=message.location.longitude)
        geolocator = Nominatim(user_agent="app_name")
        location = geolocator.reverse(f"{message.location.latitude}, {message.location.longitude}")
        await state.update_data(location_address=location)
        await bot.send_message(chat_id=message.from_user.id,
                               text=my_new_address_title_txt[language].format(location),
                               reply_markup=await get_markup_inline(language=language,
                                                                    btn_txt=yes_no_btn_txt))
        await AddressState.confirm.set()


@dp.callback_query_handler(state=AddressState.confirm)
async def confirm(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(user_id=call.from_user.id)
    user = await db.select_user(telegram=call.from_user.id)
    data = await state.get_data()
    if call.data == 'yes':
        await db.add_location(
            address=str(data['location_address']),
            longitude=float(data['longitude']),
            latitude=float(data['latitude']),
            user_id=int(user['id'])
        )
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.message.answer(success_txt[language],
                                  reply_markup=await get_markup_default(language=language, btn_txt=my_address_btn_txt))
        await AddressState.my_address.set()
    else:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        await call.message.answer(cancel_txt[language],
                                  reply_markup=await get_markup_default(language=language, btn_txt=my_address_btn_txt))
        await AddressState.my_address.set()


@dp.message_handler(text=["📜 Mening manzillarim", "📜 Мои адреса"], state=AddressState.my_address)
async def get_address(message: types.Message, state: FSMContext):
    language = await get_language(user_id=message.from_user.id)
    user = await db.select_user(telegram=message.from_user.id)
    my_address = await db.select_address_all(user_id=user['id'])

    if not my_address:
        await message.answer(empty_address_txt[language])
        await AddressState.my_address.set()
    else:
        all_address = ''
        ids = 0
        for add in my_address:
            all_address += "{}. {}\n\n".format(ids + 1, add['address'])
            ids += 1
            await state.update_data({add['id']: add['address']})
        await message.answer(delete_my_address_txt[language], reply_markup=types.ReplyKeyboardRemove())
        await message.answer(my_all_address_txt[language].format(all_address),
                             reply_markup=await get_markup_inline_delete(
                                 language=language,
                                 btn_txt=delete_adress_btn_txt,
                                 id_list=[addres['id'] for addres in my_address]
                             ))

        await state.update_data(all_address=all_address)
        await AddressState.all_address.set()


@dp.callback_query_handler(state=AddressState.all_address)
async def confirm(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(user_id=call.from_user.id)
    user = await db.select_user(telegram=call.from_user.id)
    if call.data == 'delete':
        try:
            await call.answer(text=success_txt[language], show_alert=True)
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            await db.delete_location_all(user_id=user['id'])
        except Exception as e:
            print(e)

        my_address = await db.select_address_all(user_id=user['id'])
        if not my_address:
            await call.message.answer(empty_address_txt[language],
                                      reply_markup=await get_markup_default(language=language,
                                                                            btn_txt=my_address_btn_txt))
            await AddressState.my_address.set()
        else:

            all_address = ''
            ids = 0
            for add in my_address:
                all_address += "{}. {}\n\n".format(ids + 1, add['address'])
                ids += 1
                await state.update_data({add['id']: add['address']})

            await call.message.answer(my_all_address_txt[language].format(all_address),
                                      reply_markup=await get_markup_inline_delete(
                                          language=language,
                                          btn_txt=delete_adress_btn_txt,
                                          id_list=[addres['id'] for addres in my_address]
                                      ))

            await state.update_data(all_address=all_address)
            await AddressState.all_address.set()

    elif call.data == 'address_back':
        try:
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        except Exception as e:
            print("Result:", e)

        await call.message.answer(my_address_txt[language],
                                  reply_markup=await get_markup_default(language=language, btn_txt=my_address_btn_txt))
        await AddressState.my_address.set()
    else:
        await call.answer(text=success_txt[language], show_alert=True)
        try:
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        except Exception as e:
            print("Result:", e)
        await db.delete_location(_id=int(call.data), user_id=user['id'])
        my_address = await db.select_address_all(user_id=user['id'])
        if not my_address:
            await call.message.answer(empty_address_txt[language],
                                      reply_markup=await get_markup_default(language=language,
                                                                            btn_txt=my_address_btn_txt))
            await AddressState.my_address.set()
        else:

            all_address = ''
            ids = 0
            for add in my_address:
                all_address += "{}. {}\n\n".format(ids + 1, add['address'])
                ids += 1
                await state.update_data({add['id']: add['address']})

            await call.message.answer(my_all_address_txt[language].format(all_address),
                                      reply_markup=await get_markup_inline_delete(
                                          language=language,
                                          btn_txt=delete_adress_btn_txt,
                                          id_list=[addres['id'] for addres in my_address]
                                      ))

            await state.update_data(all_address=all_address)
            await AddressState.all_address.set()
