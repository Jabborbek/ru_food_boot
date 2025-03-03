import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from geopy import Nominatim

from keyboards.inline.get_menu_keyboard import *
from loader import dp, bot, db
from func_and_message.button_text import *
from func_and_message.funcs.get_language import get_language
from func_and_message.funcs.get_markup_default import *
from func_and_message.message_text import *
from states.order import CartState
from states.userstates import AddressState
from user.utils.logging import logger


@dp.message_handler(text=["🛒 Savatcha", "🛒 Корзина"], state='*')
async def get_settings(message: types.Message, state: FSMContext):
    await state.finish()
    language = await get_language(types.User.get_current().id)
    user = await db.select_user(telegram=message.from_user.id)
    products = await db.select_user_cart_all(user_id=user['id'], status=True)

    str_a = ''
    str_products = "<b><i> {} </i></b>. <b><i> {} </i></b>➖<b><i> {} </i></b>(<b><i> {} </i></b>) x <b><i> {} </i></b> = <b><i> {} </i></b>\n"
    summa = 0
    datas = {}
    if not products:
        await message.answer(cart_empty_txt[language])
    else:
        for _id, product in enumerate(products, 1):
            p = await db.select_product_single(id=product['product_id'])
            str_a += str_products.format(_id, p['name'], product['quantity'], product['_type'],
                                         str(p['amount']).split('.')[0],
                                         "{:,}".format(int(product['quantity']) * int(p['amount'])))
            datas[f"{product['id']} ({product['_type']})"] = product['quantity']
            summa += int(product['quantity']) * int(p['amount'])
        await state.update_data(datas=datas, user_id=user['id'])
        await message.answer(cart_txt[language].format(str_a, "{:,}".format(summa)),
                             reply_markup=await get_cart_markup(cart_clear_btn_txt[language], language))
        await CartState.main.set()


@dp.callback_query_handler(state=CartState.main,
                           text=["🗑 Savatdan mahsulotni olib tashlash", "🗑 Удалить товар из корзины"])
async def back_main_menu(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    data = await state.get_data()
    await call.message.edit_reply_markup(
        reply_markup=await get_cart_delete_markup(args=data['datas'], language=language))
    await CartState.delete.set()


@dp.callback_query_handler(state=CartState.delete, text='cart_back')
async def back_main_menu(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(types.User.get_current().id)

    try:
        await call.message.edit_reply_markup(
            reply_markup=await get_cart_markup(cart_clear_btn_txt[language], language))
    except Exception as e:
        await call.message.answer(main_menu_txt[language],
                                  reply_markup=await get_markup_default_main(btn_txt=main_menu_btn_txt,
                                                                             language=language))
        await state.finish()

    await CartState.main.set()


@dp.callback_query_handler(state=CartState.delete, text='delete_all_cart')
async def back_main_menu(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    data = await state.get_data()
    try:
        await db.delete_user_cart_all_del(user_id=data.get('user_id'))
    except Exception as e:
        await call.message.answer(main_menu_txt[language],
                                  reply_markup=await get_markup_default_main(btn_txt=main_menu_btn_txt,
                                                                             language=language))
        await state.finish()
        return

    try:
        await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    except Exception as e:
        print("Error_1 :", e)

    await call.answer(success_txt[language])
    await call.message.answer(cart_empty_txt[language])
    await CartState.main.set()


@dp.callback_query_handler(state=CartState.delete)
async def back_main_menu(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    user = await db.select_user(telegram=call.from_user.id)
    if call.data.startswith('+'):
        new_quantity = call.data.split(' ')[0][1:]

        _id = call.data.split('_')[1]
        try:
            cart = await db.select_user_cart(id=int(_id))
            price_p = await db.select_product_single(id=cart['product_id'])
            await db.update_user_cart_with_id(
                quantity=str(int(new_quantity) + 1),
                user_id=user['id'],
                amount=int(price_p['amount']) * (int(new_quantity) + 1),
                _id=int(_id)
            )

            products = await db.select_user_cart_all_spets(user_id=user['id'])
            str_a = ''
            str_products = "<b><i> {} </i></b>. <b><i> {} </i></b>➖<b><i> {} </i></b>(<b><i> {} </i></b>) x <b><i> {} </i></b> = <b><i> {} </i></b>\n"
            summa = 0
            datas = {}
            if not products:
                await call.message.answer(cart_empty_txt[language])
            else:
                for _id, product in enumerate(products, 1):
                    p = await db.select_product_single(id=product['product_id'])
                    str_a += str_products.format(_id, p['name'], product['quantity'], product['_type'],
                                                 str(p['amount']).split('.')[0],
                                                 "{:,}".format(int(product['quantity']) * int(p['amount'])))
                    datas[f"{product['id']} ({product['_type']})"] = product['quantity']
                    summa += int(product['quantity']) * int(p['amount'])
                await state.update_data(datas=datas, user_id=user['id'])
                data = await state.get_data()
                await call.message.edit_text(text=cart_txt[language].format(str_a, "{:,}".format(summa)),
                                             reply_markup=await get_cart_delete_markup(args=data['datas'],
                                                                                       language=language))
                await CartState.delete.set()

        except Exception as e:
            print(e)

    elif call.data.startswith('-'):
        new_quantity = call.data.split(' ')[0][1:]
        if int(new_quantity) == 1:
            try:
                await db.delete_user_cart(_id=int(call.data.split('_')[1]), user_id=int(user['id']))
            except Exception:
                pass

            products = await db.select_user_cart_all_spets(user_id=user['id'])
            str_a = ''
            str_products = "<b><i> {} </i></b>. <b><i> {} </i></b>➖<b><i> {} </i></b>(<b><i> {} </i></b>) x <b><i> {} </i></b> = <b><i> {} </i></b>\n"
            summa = 0
            datas = {}
            if not products:
                try:
                    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
                except Exception as e:
                    pass
                await call.message.answer(cart_empty_txt[language])
            else:
                for _id, product in enumerate(products, 1):
                    p = await db.select_product_single(id=product['product_id'])
                    str_a += str_products.format(_id, p['name'], product['quantity'], product['_type'],
                                                 str(p['amount']).split('.')[0],
                                                 "{:,}".format(int(product['quantity']) * int(p['amount'])))
                    datas[f"{product['id']} ({product['_type']})"] = product['quantity']
                    summa += int(product['quantity']) * int(p['amount'])
                await state.update_data(datas=datas, user_id=user['id'])
                data = await state.get_data()
                await call.message.edit_text(text=cart_txt[language].format(str_a, "{:,}".format(summa)),
                                             reply_markup=await get_cart_delete_markup(args=data['datas'],
                                                                                       language=language))
                await CartState.delete.set()
        else:
            _id = call.data.split('_')[1]

            try:
                cart = await db.select_user_cart(id=int(_id))
                price_p = await db.select_product_single(id=cart['product_id'])
                await db.update_user_cart_with_id(
                    quantity=str(int(new_quantity) - 1),
                    amount=int(price_p['amount']) * (int(new_quantity) - 1),
                    user_id=user['id'],
                    _id=int(_id)
                )

                products = await db.select_user_cart_all_spets(user_id=user['id'])
                str_a = ''
                str_products = "<b><i> {} </i></b>. <b><i> {} </i></b>➖<b><i> {} </i></b>(<b><i> {} </i></b>) x <b><i> {} </i></b> = <b><i> {} </i></b>\n"
                summa = 0
                datas = {}
                if not products:
                    await call.message.answer(cart_empty_txt[language])
                else:
                    for _id, product in enumerate(products, 1):
                        p = await db.select_product_single(id=product['product_id'])
                        str_a += str_products.format(_id, p['name'], product['quantity'], product['_type'],
                                                     str(p['amount']).split('.')[0],
                                                     "{:,}".format(int(product['quantity']) * int(p['amount'])))
                        datas[f"{product['id']} ({product['_type']})"] = product['quantity']
                        summa += int(product['quantity']) * int(p['amount'])
                    await state.update_data(datas=datas, user_id=user['id'])
                    data = await state.get_data()
                    await call.message.edit_text(text=cart_txt[language].format(str_a, "{:,}".format(summa)),
                                                 reply_markup=await get_cart_delete_markup(args=data['datas'],
                                                                                           language=language))
                    await CartState.delete.set()

            except Exception as e:
                print(e)

    else:
        try:
            await db.delete_user_cart(_id=int(call.data.split('_')[2]), user_id=int(user['id']))
        except Exception as e:
            print(e)

        products = await db.select_user_cart_all_spets(user_id=user['id'])
        str_a = ''
        str_products = "<b><i> {} </i></b>. <b><i> {} </i></b>➖<b><i> {} </i></b>(<b><i> {} </i></b>) x <b><i> {} </i></b> = <b><i> {} </i></b>\n"
        summa = 0
        datas = {}
        if not products:
            try:
                await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            except Exception as e:
                pass
            await call.message.answer(cart_empty_txt[language])
        else:
            for _id, product in enumerate(products, 1):
                p = await db.select_product_single(id=product['product_id'])
                str_a += str_products.format(_id, p['name'], product['quantity'], product['_type'],
                                             str(p['amount']).split('.')[0],
                                             "{:,}".format(int(product['quantity']) * int(p['amount'])))
                datas[f"{product['id']} ({product['_type']})"] = product['quantity']
                summa += int(product['quantity']) * int(p['amount'])
            await state.update_data(datas=datas, user_id=user['id'])
            data = await state.get_data()

            await call.message.edit_text(text=cart_txt[language].format(str_a, "{:,}".format(summa)),
                                         reply_markup=await get_cart_delete_markup(args=data['datas'],
                                                                                   language=language))
            await CartState.delete.set()


@dp.callback_query_handler(state=CartState.main,
                           text=["💳 Buyurtma berish", "💳 Оформить заказ"])
async def back_main_menu(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    data = await state.get_data()
    try:
        await bot.delete_message(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
    except Exception as e:
        print(e)

    if data.get('select_address') is None:
        try:
            user = await db.select_user(telegram=call.from_user.id)
            products = await db.select_user_cart_all(user_id=user['id'], status=True)
            summa = [int(s['amount']) for s in products]
            amount = sum(summa) * 100

            order = await db.add_order(
                user_id=int(data.get('user_id')),
                address_id=None,
                distance=None,
                payment_type=str(0),
                admin_status=str(0),
                amount=amount,
                pay_type=f'{call.data}',
                status=True,
                create_date=datetime.datetime.now())

            for i in data.get('datas').keys():
                pro_id = await db.select_user_cart(id=int(i.split(' ')[0]))

                await db.add_ordersale(
                    order_id=order.get('id'),
                    product_id=int(pro_id['product_id']),
                    quantity=int(pro_id['quantity']),
                    user_id=int(pro_id['user_id']),
                    amount=int(pro_id['amount']),
                    _type=pro_id['_type'],
                    create_date=datetime.datetime.now())
            await call.message.answer(cash_success_txt[language],
                                      reply_markup=await get_markup_default_main(btn_txt=main_menu_btn_txt,
                                                                                 language=language))

            try:

                products = await db.select_user_cart_all_spets(user_id=data.get('user_id'))
                user = await db.select_user(telegram=call.from_user.id)
                summa = [int(s['amount']) for s in products]

                str_a = ''
                product_text = "<b><i>{}</i></b>) <b><i>{}</i></b> - <b><i>{} ({})</i></b> x <b><i>{}</i></b> = <b><i>{}</i></b> {}\n"
                max_time = []
                for _id, product in enumerate(products, 1):
                    p = await db.select_product_single(id=product['product_id'])

                    max_time.append(p['time'])
                    str_a += product_text.format(_id,
                                                 p['name'],
                                                 product['quantity'],
                                                 product['_type'],
                                                 str(p['amount']).split('.')[0],
                                                 "{:,}".format(int(product['quantity']) * int(p['amount'])),
                                                 p_type_txt[language])
                all_summ = "{:,}".format(int(sum(summa)))
                await bot.send_message(
                    chat_id='-1002009458747',
                    text=cash_order_text[language].format(
                        datetime.datetime.now().strftime('%Y-%m-%d, %H:%M:%S'),
                        user['fullname'],
                        user['phone'],
                        str_a,
                        all_summ,
                        all_summ,
                        status_pay_type_txt[language][1]))
                geolocator = Nominatim(user_agent="app_name")
                location = geolocator.reverse(f"{41.324012}, {69.315419}")
                await bot.send_venue(
                    chat_id=call.from_user.id,
                    latitude=41.324012,
                    longitude=69.315419,
                    title=address_title_text[language],
                    address=location
                )
            except Exception as e:
                logger.error('cash error message: {}'.format(e))

            try:
                await db.delete_user_cart_all(user_id=int(data.get('user_id')))
            except Exception as e:
                logger.error('cash error message: Delete error: {}'.format(e))

            await state.finish()
        except Exception as e:
            logger.error('cash error message: {}'.format(e))


