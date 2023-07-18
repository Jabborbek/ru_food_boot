from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.inline.get_menu_keyboard import *
from loader import dp, bot, db
from messages.button_text import *
from messages.funcs.get_language import get_language
from messages.funcs.get_markup_default import *
from messages.message_text import *
from states.order import CartState
from states.userstates import AddressState


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
                                         str(p['price']).split('.')[0],
                                         "{:,}".format(int(product['quantity']) * int(p['price'])))
            datas[f"{product['id']} ({product['_type']})"] = product['quantity']
            summa += int(product['quantity']) * int(p['price'])
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
                price=int(price_p['price']) * (int(new_quantity) + 1),
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
                                                 str(p['price']).split('.')[0],
                                                 "{:,}".format(int(product['quantity']) * int(p['price'])))
                    datas[f"{product['id']} ({product['_type']})"] = product['quantity']
                    summa += int(product['quantity']) * int(p['price'])
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
                                                 str(p['price']).split('.')[0],
                                                 "{:,}".format(int(product['quantity']) * int(p['price'])))
                    datas[f"{product['id']} ({product['_type']})"] = product['quantity']
                    summa += int(product['quantity']) * int(p['price'])
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
                    price=int(price_p['price']) * (int(new_quantity) - 1),
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
                                                     str(p['price']).split('.')[0],
                                                     "{:,}".format(int(product['quantity']) * int(p['price'])))
                        datas[f"{product['id']} ({product['_type']})"] = product['quantity']
                        summa += int(product['quantity']) * int(p['price'])
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
                                             str(p['price']).split('.')[0],
                                             "{:,}".format(int(product['quantity']) * int(p['price'])))
                datas[f"{product['id']} ({product['_type']})"] = product['quantity']
                summa += int(product['quantity']) * int(p['price'])
            await state.update_data(datas=datas, user_id=user['id'])
            data = await state.get_data()

            await call.message.edit_text(text=cart_txt[language].format(str_a, "{:,}".format(summa)),
                                         reply_markup=await get_cart_delete_markup(args=data['datas'],
                                                                                   language=language))
            await CartState.delete.set()


@dp.callback_query_handler(state=CartState.main,
                           text=["💳 Официальное оформление", "💳 Rasmiyalshtirish"])
async def back_main_menu(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    await call.message.edit_reply_markup(
        reply_markup=await get_cart_markup_2(args=dastavka_btn_txt[language], language=language))
    await CartState.officialization.set()


@dp.callback_query_handler(state=CartState.officialization,
                           text=["🔙 Orqaga", "🔙 Назад"])
async def back_main_menu(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    await call.message.edit_reply_markup(
        reply_markup=await get_cart_markup(cart_clear_btn_txt[language], language))
    await CartState.main.set()


@dp.callback_query_handler(state=CartState.officialization,
                           text=["🚶 Borib olish", "🚶 Самовывоз"])
async def back_main_menu(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    user = await db.select_user(telegram=call.from_user.id)
    try:
        await call.message.edit_text(text=payments_type[language],
                                     reply_markup=await get_payments_markup(args=payments_btn_txt[language],
                                                                            language=language))

        user = await db.select_user(telegram=call.from_user.id)
        products = await db.select_user_cart_all(user_id=user['id'], status=True)
        summa = [int(s['price']) for s in products]
        await state.update_data(a_status=call.data, summa=sum(summa))
        await CartState.payments.set()
    except Exception as e:
        print("Officialization error:", e)


@dp.callback_query_handler(state=CartState.officialization,
                           text=["🛵 Yetkazib berish", "🛵 Доставка"])
async def back_main_menu(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    user = await db.select_user(telegram=call.from_user.id)
    all_address = await db.select_address_all(user_id=user['id'])
    if not all_address:
        try:
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        except Exception as e:
            print("Error_1 :", e)
        await call.message.answer(text=empty_address_txt[language],
                                  reply_markup=await get_markup_default(language=language, btn_txt=my_address_btn_txt))
        await AddressState.my_address.set()
    else:
        all_address_text = ''
        address_text = '{})📍 {}\n'
        address_dict = {}
        for index, address in enumerate(all_address, 1):
            all_address_text += address_text.format(index, address['address'])
            address_dict[address['id']] = index
        await state.update_data(address=address_dict, a_status=call.data)
        await call.message.edit_text(dastavka_txt[language].format(all_address_text),
                                     reply_markup=await get_dastavka_markup(args=address_dict, language=language))
        await CartState.dastavka.set()


@dp.callback_query_handler(state=CartState.dastavka)
async def back_main_menu(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    summa = 0
    user = await db.select_user(telegram=call.from_user.id)
    products = await db.select_user_cart_all(user_id=user['id'], status=True)
    str_a = ''
    str_products = "<b><i> {} </i></b>. <b><i> {} </i></b>➖<b><i> {} </i></b>(<b><i> {} </i></b>) x <b><i> {} </i></b> = <b><i> {} </i></b>\n"
    datass = {}

    if call.data == 'das_back':

        if not products:
            try:
                await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            except Exception as e:
                print("Error_1 :", e)
            await call.message.answer(cart_empty_txt[language])
        else:
            for _id, product in enumerate(products, 1):
                p = await db.select_product_single(id=product['product_id'])
                str_a += str_products.format(_id, p['name'], product['quantity'], product['_type'],
                                             str(p['price']).split('.')[0],
                                             "{:,}".format(int(product['quantity']) * int(p['price'])))
                datass[_id] = product['id']
                summa += int(product['quantity']) * int(p['price'])
            await state.update_data(datass=datass, user_id=user['id'], summa=summa)
            await call.message.edit_text(text=cart_txt[language].format(str_a, "{:,}".format(summa)),
                                         reply_markup=await get_cart_markup_2(args=dastavka_btn_txt[language],
                                                                              language=language))
            await CartState.officialization.set()
    else:
        for _id, product in enumerate(products, 1):
            p = await db.select_product_single(id=product['product_id'])
            str_a += str_products.format(_id, p['name'], product['quantity'], product['_type'],
                                         str(p['price']).split('.')[0],
                                         "{:,}".format(int(product['quantity']) * int(p['price'])))
            datass[_id] = product['id']
            summa += int(product['quantity']) * int(p['price'])
        await state.update_data(datass=datass, user_id=user['id'], summa=summa, select_address=call.data)

        await call.message.edit_text(text=payments_type[language],
                                     reply_markup=await get_payments_markup(args=payments_btn_txt[language],
                                                                            language=language))
        await CartState.payments.set()
