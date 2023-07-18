from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, db
from messages.button_text import p_type_txt
from messages.funcs.get_language import get_language
from messages.message_text import *


@dp.message_handler(text=['📦 Buyurtmalarim', '📦 Мои заказы'], state='*')
async def get_settings(message: types.Message, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    user = await db.select_user(telegram=message.from_user.id)
    products = await db.select_user_order_all_sorted(user_id=user['id'])
    if not products:
        await message.answer(empty_order_txt[language])
        await state.finish()
    else:
        unique_dates = sorted(set(item['create_date'] for item in products))
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

        D = [[item for item in products if item['create_date'] == dt] for dt in unique_dates]
        product_text = "<b><i>{}</i></b>) <b><i>{}</i></b> - <b><i>{}</i></b> x <b><i>{}</i></b> = <b><i>{}</i></b> {}\n"

        str_order = {
            "uz": "⏰ <b><i>[{}]</i></b>\n\n"
                  "{}\n\n"
                  "🧮 Umumiy xarajat:  <b><i>{}</i></b> so'm\n"
                  "💡Holat:   {}\n\n"
                  "🔸🔸🔸🔹🔹🔹🔸🔸🔸🔹🔹🔹\n\n",
            "ru": "⏰ <b><i>[{}]</i></b>\n\n"
                  "{}\n\n"
                  "🧮 Общая стоимость: <b><i>{}</i></b> сум\n"
                  "💡Статус: {}\n\n"
                  "🔸🔸🔸🔹🔹🔹🔸🔸🔸🔹🔹🔹\n\n"
        }

        result_order = ""
        status = ""
        s = 0
        time = ""

        for d in D:
            products_text = ""
            for index, pro in enumerate(d, 1):
                pro_name = await db.select_product_single(id=int(pro['product_id']))
                time = pro['create_date']
                s += int(pro['price'])
                status = pro['admin_status']
                products_text += product_text.format(index, pro_name[f'name_{language}'],
                                                     f"{pro['quantity']} ({pro['_type']})",
                                                     str(pro_name['price']).split('.')[0],
                                                     "{:,}".format(int(pro['price'])), p_type_txt[language])

            result_order += str_order[language].format(time, products_text, "{:,}".format(s), choice[language][status])
            s = 0

        await message.answer(pay_success_order_txt[language].format(result_order))
        await state.finish()
