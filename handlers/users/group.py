import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import LabeledPrice

from filters.filter import is_admin
from keyboards.inline.get_menu_keyboard import *
from loader import dp, bot, db
from messages.button_text import *
from messages.funcs.get_distance import get_distance_km
from messages.funcs.get_language import get_language
from messages.funcs.get_markup_default import *
from messages.message_text import *
from utils.misc.product import Product


@dp.callback_query_handler(is_admin(), lambda q: q.data.startswith('🟠 Tasdiqlash kutilmoqda') or q.data.startswith(
    "🟠 Ожидается подтверждение"))
async def check_button(call: types.CallbackQuery):
    print(call.data)
    user_id = call.data.split('_')[1]
    language_user = await get_language(user_id=int(user_id))
    try:
        await call.message.edit_reply_markup(
            await get_order_admin_markup(succes_btn_succes_txt[language_user], user_id=user_id))
        try:
            await bot.send_message(chat_id=user_id, text=cash_confirm_admin_text[language_user])
        except Exception as e:
            print('Update error: ', e)
    except Exception as e:
        print("Error confirm: ", e)
