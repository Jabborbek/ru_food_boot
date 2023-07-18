import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.inline.get_menu_keyboard import *
from loader import dp, bot, db
from messages.button_text import *
from messages.funcs.check_user import check_id
from messages.funcs.get_language import get_language
from messages.funcs.get_markup_default import *
from messages.message_text import *
from states.order import OrderState


@dp.message_handler(text=["🛍 Buyurtma berish", "🛍 Начать заказ"], state='*')
async def get_settings(message: types.Message, state: FSMContext):
    await state.finish()
    language = await get_language(types.User.get_current().id)
    categories = await db.select_category()
    if not categories:
        await message.answer(category_empty_txt[language])
    else:
        await message.answer(category_txt[language], reply_markup=types.ReplyKeyboardRemove())
        await message.answer(text=category_menu_txt[language],
                             reply_markup=await get_category_markup(categories=categories, language=language))

        await OrderState.category.set()


@dp.callback_query_handler(text='cat_back', state=OrderState.category)
async def back_main_menu(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    except Exception:
        pass
    await call.message.answer(main_menu_txt[language],
                              reply_markup=await get_markup_default_main(btn_txt=main_menu_btn_txt,
                                                                         language=language))
    await state.finish()


@dp.callback_query_handler(state=OrderState.category)
async def get_cat_menu(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    products = await db.select_product(category_id=int(call.data))
    if not products:
        await call.answer(not_products_txt[language], show_alert=True)
    else:
        try:
            await call.message.edit_text(text=products_txt[language],
                                         reply_markup=await get_product_markup(products=products, language=language))
            await state.update_data(category_id=call.data)
            await OrderState.product.set()
        except Exception:
            await call.message.answer(main_menu_txt[language],
                                      reply_markup=await get_markup_default_main(btn_txt=main_menu_btn_txt,
                                                                                 language=language))
            await state.finish()


@dp.callback_query_handler(text='cat_back', state=OrderState.product)
async def back_main_menu(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    categories = await db.select_category()
    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    except Exception:
        pass
    await call.message.answer(text=category_menu_txt[language],
                              reply_markup=await get_category_markup(categories=categories, language=language))

    await OrderState.category.set()


@dp.callback_query_handler(state=OrderState.product)
async def get_cat_menu(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    products = await db.select_product(id=int(call.data))

    user_product_measure = await db.select_user_product_measure(product_id=int(call.data))
    aaa = [[{m[f'name_{language}']: m['id']}
            for m in await db.select_user_measure(
            id=int(meas['measure_id']))][0] for meas in
           user_product_measure]

    if not products:
        pass
    else:
        try:
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        except Exception as e:
            print("Error_1 :", e)
        try:
            await bot.send_photo(chat_id=call.from_user.id,
                                 photo=types.InputFile(path_or_bytesio=f"app/{products[0]['image']}"),
                                 caption=order_product_txt[language].format(products[0][f"name_{language}"],
                                                                            str(products[0]['price']).split('.')[0],
                                                                            products[0][f'description_{language}']),
                                 reply_markup=await get_order_markup(args=[[m[f'name_{language}']
                                                                            for m in await db.select_user_measure(
                                         id=int(meas['measure_id']))][0] for meas in
                                                                           user_product_measure],
                                                                     language=language))
            await state.update_data(product_id=call.data, aaa=aaa, birlik=[[m[f'name_{language}']
                                                                            for m in await db.select_user_measure(
                    id=int(meas['measure_id']))][0] for meas in
                                                                           user_product_measure])
            await OrderState.measure.set()
        except Exception as e:
            print("Error_2 :", e)


@dp.callback_query_handler(text='order_back', state=OrderState.measure)
async def back_main_menu(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    data = await state.get_data()
    products = await db.select_product(category_id=int(data.get('category_id')))

    if not products:
        await call.answer(not_products_txt[language], show_alert=True)
    else:
        try:
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        except Exception as e:
            print("Error_1 :", e)
        try:
            await call.message.answer(text=products_txt[language],
                                      reply_markup=await get_product_markup(products=products, language=language))
            await OrderState.product.set()
        except Exception as e:
            print("Error_3 :", e)
            await call.message.answer(main_menu_txt[language],
                                      reply_markup=await get_markup_default_main(btn_txt=main_menu_btn_txt,
                                                                                 language=language))
            await state.finish()


@dp.callback_query_handler(state=OrderState.measure)
async def back_main_menu(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    data = await state.get_data()
    measure_id = check_id(args=data.get('aaa'), call=call.data)
    quantity = await db.select_user_productquantity(measure_id=int(measure_id))

    try:
        await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            reply_markup=await get_measure_markup(
                                                args=str(quantity['quantity']).split('.')[0],
                                                language=language))
        await state.update_data(quantity=str(quantity['quantity']).split('.')[0],
                                increment=str(quantity['quantity']).split('.')[0],
                                _type=call.data)
        await OrderState.quantity.set()
    except Exception as e:
        print("Error_4 :", e)
        await call.message.answer(main_menu_txt[language],
                                  reply_markup=await get_markup_default_main(btn_txt=main_menu_btn_txt,
                                                                             language=language))
        await state.finish()


@dp.callback_query_handler(text='cat_back', state=OrderState.quantity)
async def back_main_menu(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    data = await state.get_data()

    try:
        await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            reply_markup=await get_order_markup(
                                                args=data.get('birlik'),
                                                language=language))
        await OrderState.measure.set()
    except Exception as e:
        print("Error_3 :", e)
        await call.message.answer(main_menu_txt[language],
                                  reply_markup=await get_markup_default_main(btn_txt=main_menu_btn_txt,
                                                                             language=language))
        await state.finish()


@dp.callback_query_handler(state=OrderState.quantity)
async def back_main_menu(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    data = await state.get_data()
    quantity = data.get('quantity')
    increment = data.get('increment')
    if call.data == '+':
        quantity = float(quantity) + float(increment)
        await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            reply_markup=await get_measure_markup(args=str(quantity).split('.')[0],
                                                                                  language=language))
        await state.update_data(quantity=str(quantity).split('.')[0])
        await OrderState.quantity.set()

    elif call.data == '-':
        if float(quantity) > float(increment):
            quantity = float(quantity) - float(increment)
            await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                                reply_markup=await get_measure_markup(args=str(quantity).split('.')[0],
                                                                                      language=language))
            await state.update_data(quantity=str(quantity).split('.')[0])
            await OrderState.quantity.set()
        else:
            await call.answer(products_quantity_txt[language])
            await OrderState.quantity.set()
    elif call.data == 'add_cart':
        await call.answer(cache_time=5)
        user = await db.select_user(telegram=call.from_user.id)

        try:

            price_product = await db.select_product_single(id=int(data.get('product_id')))
            await db.add_cart(
                user_id=user['id'],
                product_id=int(data.get('product_id')),
                _type=data.get('_type'),
                quantity=data.get('quantity'),
                price=int(data.get('quantity')) * int(price_product['price']),
                status=True,
                create_date=datetime.datetime.now()
            )
            try:
                await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            except Exception as e:
                print("Error_6 :", e)

            await call.message.answer(retry_products_txt[language],
                                      reply_markup=await get_markup_default_main(btn_txt=main_menu_btn_txt,
                                                                                 language=language))
            await state.finish()

        except Exception as e:
            print("Error_5_ :", e)

    else:
        await call.answer(cache_time=5)
