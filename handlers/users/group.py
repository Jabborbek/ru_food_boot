from aiogram import types

from filters.filter import is_admin
from keyboards.inline.get_menu_keyboard import *
from loader import dp, bot, db
from func_and_message.button_text import *
from func_and_message.funcs.get_language import get_language
from func_and_message.message_text import *


@dp.callback_query_handler(is_admin(), lambda q: q.data.startswith('✅ Tasdiqlash') or q.data.startswith(
    "✅ Подтверждение"))
async def check_button(call: types.CallbackQuery):
    user_id = call.data.split('_')[1]
    order_id = call.data.split('_')[2]
    d_type = call.data.split('_')[3]
    time = call.data.split('_')[4]
    language_user = await get_language(user_id=int(user_id))
    await db.update_user_order_with_id(admin_status="1", _id=int(order_id))
    try:
        await call.message.edit_reply_markup(
            await get_order_admin_markup(succes_btn_succes_txt[language_user], user_id=user_id, order_id=int(order_id), d_type=int(d_type), time=int(time)))
        try:
            if int(d_type) == 1:
                await bot.send_message(chat_id=user_id, text=cash_confirm_admin_text[language_user].format(order_id, time))
            else:
                await bot.send_message(chat_id=user_id, text=payme_confirm_admin_text[language_user].format(order_id, time))
        except Exception as e:
            print('Update error: ', e)
    except Exception as e:
        print("Error confirm in group: ", e)


@dp.callback_query_handler(is_admin(), lambda q: q.data.startswith('❌ Bekor qilish') or q.data.startswith(
    "❌ Отмена"))
async def check_button(call: types.CallbackQuery):
    user_id = call.data.split('_')[1]
    order_id = call.data.split('_')[2]
    d_type = call.data.split('_')[3]
    time = call.data.split('_')[4]
    language_user = await get_language(user_id=int(user_id))
    await db.update_user_order_with_id(admin_status="2", _id=int(order_id))
    try:
        await call.message.edit_reply_markup(
            await get_order_admin_markup(feedback_cancel_btn_txt[language_user], user_id=user_id,
                                         order_id=int(order_id),
                                         d_type=d_type,
                                         time=time))
        try:
            await bot.send_message(chat_id=user_id, text=cash_cancel_admin_text[language_user].format(order_id))
        except Exception as e:
            print('Update error: ', e)
    except Exception as e:
        print("Error confirm: ", e)
