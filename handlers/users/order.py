from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageIsTooLong

from func_and_message.button_text import p_type_txt
from func_and_message.funcs.get_language import get_language
from func_and_message.message_text import *
from loader import dp, db, bot
from user.utils.logging import logger


async def send_long_message(chat_id, text, parse_mode: types.ParseMode.HTML):
    MAX_MESSAGE_LENGTH = 4096
    chunks = [text[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(text), MAX_MESSAGE_LENGTH)]
    for chunk in chunks:
        await bot.send_message(chat_id, chunk)


@dp.message_handler(text=['📦 Buyurtmalarim', '📦 Мои заказы'], state='*')
async def get_settings(message: types.Message, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    user = await db.select_user(telegram=message.from_user.id)
    orders = await db.select_user_order_all_sorted(user_id=user['id'])

    if not orders:
        await message.answer(empty_order_txt[language])
        await state.finish()
    else:
        choice = {
            "uz": {
                "0": "🟠 Tasdiqlash kutilmoqda",
                "1": "🟢 Tasdiqlandi",
                "2": "🔴 Bekor qilindi"
            },
            "ru": {
                "0": "🟠 Ожидается подтверждение",
                "1": "🟢 Подтверждено",
                "2": "🔴 Отменено"
            },
        }
        payments_status = {
            "uz": {
                "0": "🟠 To'lov kutilmoqda",
                "1": "🟢 To'lov qilindi",
                "2": "🔴 Bekor qilindi"
            },
            "ru": {
                "0": "🟠 Ожидает оплаты",
                "1": "🟢 Оплачено",
                "2": "🔴 Отменено"
            },
        }

        product_text = "<b><i>{}</i></b>) <b><i>{}</i></b> - <b><i>{}</i></b> x <b><i>{}</i></b> = <b><i>{}</i></b> {}\n"
        str_order = {
            "uz": "Buyurtma raqami: #<b><i>{}</i></b>\n\n"
                  "⏰ <b><i>[{}]</i></b>\n\n"
                  "{}\n\n"
                  "🧮 Umumiy xarajat:  <b><i>{}</i></b> so'm\n\n"
                  "🔸🔸🔸🔹🔹🔹🔸🔸🔸🔹🔹🔹\n\n",
            "ru": "Номер заказа: #<b><i>{}</i></b>\n\n"
                  "⏰ <b><i>[{}]</i></b>\n\n"
                  "{}\n\n"
                  "🧮 Общая стоимость: <b><i>{}</i></b> сум\n\n"
                  "🔸🔸🔸🔹🔹🔹🔸🔸🔸🔹🔹🔹\n\n"
        }

        result_order = ""
        status = ""
        s = 0
        time = ""

        for order in orders:
            products = await db.select_user_order_sale_all_sorted(user_id=user['id'], order_id=order.get('id'))
            products_text = ""
            for index, pro in enumerate(products, 1):
                pro_name = await db.select_product_single(id=int(pro['product_id']))
                time = pro['create_date']
                s += int(pro['amount'])
                status = order['admin_status']
                products_text += product_text.format(index, pro_name[f'name_{language}'],
                                                     f"{pro['quantity']} ({pro['_type']})",
                                                     str(pro_name['amount']).split('.')[0],
                                                     "{:,}".format(int(pro['amount'])), p_type_txt[language])

            result_order += str_order[language].format(order.get('id'), time, products_text, "{:,}".format(s),
                                                       choice[language][status],
                                                       payments_status[language][order['payment_type']])
            s = 0

        try:
            await send_long_message(message.from_user.id, pay_success_order_txt[language].format(result_order), 'html')
        except MessageIsTooLong as e:
            logger.error(f"Error sending long message: {e}")

        await state.finish()
