from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.inline.get_menu_keyboard import _markup
from loader import dp, db, bot
from states.order import OrderState


@dp.callback_query_handler(state=OrderState.product)
async def get_product(call: types.CallbackQuery, state: FSMContext):
    product = await db.select_product_single(id=call.data)
    if not product:
        await call.answer(
            text='Не найдено информации для этого продукта', show_alert=True
        )
    else:
        try:
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        except Exception:
            pass

        await bot.send_photo(
            chat_id=call.from_user.id,
            photo=types.InputFile(path_or_bytesio=f"media/{product['image']}"),
            caption=f"💵 Цена продукта: {str(product['price']).split('.')[0]} rubl\n\nℹ️ О продукте: {product['description']}",
            reply_markup=await _markup()
        )

        await OrderState.back_product.set()
