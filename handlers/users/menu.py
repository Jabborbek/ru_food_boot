from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.default.main_kb import main_menu_kb
from keyboards.inline.get_menu_keyboard import *
from loader import dp, db, bot
from states.order import OrderState


@dp.message_handler(text='🛍 Продукты', state='*')
async def get_category(message: types.Message, state: FSMContext):
    await state.finish()
    categories = await db.select_category()
    if not categories:
        try:
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        except Exception:
            pass
        await message.answer(
            "К сожалению, категория еще не создана!"
        )
    else:
        await message.answer('Пожалуйста, выберите категорию.',
                             reply_markup=await get_category_markup(categories=categories))

        await OrderState.category.set()


@dp.callback_query_handler(text='cat_back', state=OrderState.category)
async def get_category(call: types.CallbackQuery, state: FSMContext):
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    except Exception:
        pass

    await call.message.answer(
        text='Привет и добро пожаловать!',
        reply_markup=main_menu_kb
    )

    await state.finish()


@dp.callback_query_handler(state=OrderState.category)
async def get_category(call: types.CallbackQuery, state: FSMContext):
    subcategories = await db.select_subcategory_where(category_id=call.data)
    if not subcategories:

        await call.answer(
            text='Эта категория пуста', show_alert=True
        )
    else:
        await call.message.edit_text(
            text='Выберите подкатегорию.',
            reply_markup=await get_subcategory_markup(
                subcategories=subcategories
            )
        )
        await state.update_data(cat_id=call.data)
        await OrderState.subcategory.set()


@dp.callback_query_handler(text='sub_cat_back', state=OrderState.subcategory)
async def get_category(call: types.CallbackQuery, state: FSMContext):
    categories = await db.select_category()
    if not categories:
        try:
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        except Exception:
            pass
        await call.message.answer(
            "К сожалению, категория еще не создана!", reply_markup=main_menu_kb
        )
        await state.finish()
    else:
        await call.message.edit_text(
            'Пожалуйста, выберите категорию.',
            reply_markup=await get_category_markup(categories=categories)
        )

        await OrderState.category.set()


@dp.callback_query_handler(state=OrderState.subcategory)
async def get_products(call: types.CallbackQuery, state: FSMContext):
    products = await db.select_product(subcategory_id=call.data, status=True)
    if not products:

        await call.answer(
            text='Эта подкатегория пуста', show_alert=True
        )
    else:
        await call.message.edit_text(
            text='Пожалуйста, выберите продукт!',
            reply_markup=await get_product_markup(
                products=products
            )
        )
        await state.update_data(sub_id=call.data)
        await OrderState.product.set()


@dp.callback_query_handler(text='product_back', state=OrderState.product)
async def get_category(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    subcategories = await db.select_subcategory_where(category_id=data.get('cat_id'))
    if not subcategories:
        try:
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        except Exception:
            pass

        await call.message.answer(
            text='Эта подкатегория пуста', reply_markup=main_menu_kb
        )
        await state.finish()
    else:
        await call.message.edit_text(
            text='Выберите подкатегорию.',
            reply_markup=await get_subcategory_markup(
                subcategories=subcategories
            )
        )
        await OrderState.subcategory.set()
