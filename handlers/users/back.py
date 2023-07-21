from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.default.main_kb import main_menu_kb
from keyboards.inline.get_menu_keyboard import *
from loader import dp, db, bot
from states.order import OrderState


@dp.callback_query_handler(text='main_main', state='*')
async def get_product(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    except Exception:
        pass

    await call.message.answer(
        text='Привет и добро пожаловать!',
        reply_markup=main_menu_kb
    )


@dp.callback_query_handler(text='bac_main', state=OrderState.back_product)
async def get_product(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    products = await db.select_product(subcategory_id=data.get('sub_id'), status=True)
    if not products:
        await call.answer(
            text='Эта подкатегория пуста', show_alert=True
        )
    else:
        try:
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        except Exception:
            pass
        await call.message.answer(
            text='Пожалуйста, выберите продукт!',
            reply_markup=await get_product_markup(
                products=products
            )
        )
        await OrderState.product.set()
