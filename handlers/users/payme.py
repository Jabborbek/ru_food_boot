import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import LabeledPrice, PreCheckoutQuery, ContentType
from geopy.geocoders import Nominatim
from data import config
from keyboards.inline.get_menu_keyboard import *
from loader import dp, bot, db
from messages.button_text import *
from messages.funcs.get_distance import get_distance_km
from messages.funcs.get_language import get_language
from messages.funcs.get_markup_default import *
from messages.message_text import *
from states.order import CartState
from utils.misc.product import Product


@dp.callback_query_handler(text='💳 Payme', state=CartState.payments)
async def praktikum_invoice(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = await get_language(call.from_user.id)
    if data.get('select_address') is None:
        print('Payme:', data)
        try:
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        except Exception as e:
            print("Error_1 :", e)

        product = Product(
            title=payme_title[language],
            description=payme_description[language].format(0, 0),
            currency="UZS",
            prices=[
                LabeledPrice(
                    label=payme_title[language],
                    amount=int(data.get('summa')) * 100,
                )
            ],
            start_parameter="create_invoice_product",
            need_name=True,
            need_phone_number=True,

        )

        await bot.send_invoice(chat_id=call.from_user.id,
                               **product.generate_invoice(),
                               payload="payload:product")
        await call.answer()
        await state.reset_state(with_data=False)
    else:
        address = await db.select_address_(id=int(data.get('select_address')))
        distance = get_distance_km(location=(address['latitude'], address['longitude']))

        try:
            await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
        except Exception as e:
            print("Error_1 :", e)

        price = await db.select_dastavka_(qiymat=distance)
        if price is None:
            await call.message.answer(payme_no_distance[language],
                                      reply_markup=await get_markup_default_main(btn_txt=main_menu_btn_txt,
                                                                                 language=language))
            await state.finish()
            return
        else:
            product = Product(
                title=payme_title[language],
                description=payme_description[language].format(f"{distance:.2f}", "{:,}".format(int(price['price']))),
                currency="UZS",
                prices=[
                    LabeledPrice(
                        label=payme_title[language],
                        amount=int(int(data.get('summa')) + int(price['price'])) * 100,
                    )
                ],
                start_parameter="create_invoice_product",
                need_name=True,
                need_phone_number=True,

            )

            await bot.send_invoice(chat_id=call.from_user.id,
                                   **product.generate_invoice(),
                                   payload="payload:product")
            await call.answer()
            await state.reset_state(with_data=False)

        # try:
        #
        #     address = await db.select_address_(id=int(data.get('select_address')))
        #     products = await db.select_user_cart_all_spets(user_id=data.get('user_id'))
        #     user = await db.select_user(telegram=call.from_user.id)
        #     summa = [int(s['price']) for s in products]
        #
        #     str_a = ''
        #     product_text = "<b><i>{}</i></b>) <b><i>{}</i></b> - <b><i>{} {})</i></b> x <b><i>{}</i></b> = <b><i>{}</i></b> {}\n"
        #
        #     for _id, product in enumerate(products, 1):
        #         p = await db.select_product_single(id=product['product_id'])
        #         str_a += product_text.format(_id,
        #                                      p['name'],
        #                                      product['quantity'],
        #                                      product['_type'],
        #                                      str(p['price']).split('.')[0],
        #                                      "{:,}".format(int(product['quantity']) * int(p['price'])),
        #                                      p_type_txt[language])
        #     all_summ = "{:,}".format(int(price['price']) + int(sum(summa)))
        #     await bot.send_message(chat_id='-1001634768280', text=new_order_text[language].format(
        #         datetime.datetime.now().strftime('%Y-%m-%d, %H:%M:%S'),
        #         user['fullname'],
        #         user['phone'],
        #         str_a,
        #         "{:,}".format(sum(summa)),
        #         'Payme',
        #         address['address'],
        #         data.get('a_status'),
        #         f"{distance:.2f}",
        #         "{:,}".format(int(price['price'])),
        #         all_summ,
        #         status_pay_type_txt[language][0]), reply_markup=await get_order_admin_markup(succes_btn_txt[language],
        #                                                                                      user_id=call.from_user.id))
        # except Exception as e:
        #     print("Send message error:", e)


@dp.pre_checkout_query_handler(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message, state: FSMContext):
    language = await get_language(message.from_user.id)
    data = await state.get_data()
    if data.get('select_address') is None:
        try:
            for i in data.get('datas').keys():
                pro_id = await db.select_user_cart(id=int(i.split(' ')[0]))
                await db.add_order(product_id=int(pro_id['product_id']),
                                   quantity=int(pro_id['quantity']),
                                   user_id=int(pro_id['user_id']),
                                   address_id=None,
                                   payment_type=str(2),
                                   admin_status=str(0),
                                   price=int(pro_id['price']),
                                   pay_type='payme',
                                   _type=pro_id['_type'],
                                   status=True,
                                   a_status=data.get('a_status'),
                                   create_date=datetime.datetime.now())
            await message.answer(pay_cash_success_txt[language],
                                 reply_markup=await get_markup_default_main(btn_txt=main_menu_btn_txt,
                                                                            language=language))

            try:

                products = await db.select_user_cart_all_spets(user_id=data.get('user_id'))
                user = await db.select_user(telegram=message.from_user.id)
                summa = [int(s['price']) for s in products]

                str_a = ''
                product_text = "<b><i>{}</i></b>) <b><i>{}</i></b> - <b><i>{} ({})</i></b> x <b><i>{}</i></b> = <b><i>{}</i></b> {}\n"

                for _id, product in enumerate(products, 1):
                    p = await db.select_product_single(id=product['product_id'])
                    str_a += product_text.format(_id,
                                                 p['name'],
                                                 product['quantity'],
                                                 product['_type'],
                                                 str(p['price']).split('.')[0],
                                                 "{:,}".format(int(product['quantity']) * int(p['price'])),
                                                 p_type_txt[language])
                all_summ = "{:,}".format(int(sum(summa)))
                await bot.send_message(chat_id='-1001634768280', text=cash_order_text[language].format(
                    datetime.datetime.now().strftime('%Y-%m-%d, %H:%M:%S'),
                    user['fullname'],
                    user['phone'],
                    str_a,
                    "{:,}".format(sum(summa)),
                    'Payme',
                    data.get('a_status'),
                    all_summ,
                    status_pay_type_txt[language][0]),
                                       reply_markup=await get_order_admin_markup(succes_btn_txt[language],
                                                                                 user_id=message.from_user.id))
                geolocator = Nominatim(user_agent="app_name")
                location = geolocator.reverse(f"{41.324012}, {69.315419}")
                await bot.send_venue(
                    chat_id=message.from_user.id,
                    latitude=41.324012,
                    longitude=69.315419,
                    title=address_title_text[language],
                    address=location
                )
            except Exception as e:
                print("Send message error:", e)

            try:
                await db.delete_user_cart_all(user_id=int(data.get('user_id')))
            except Exception:
                pass

            await state.finish()
        except Exception as e:
            print('Payme Error_1:', e)
    else:
        try:
            for i in data.get('datas').keys():
                pro_id = await db.select_user_cart(id=int(i.split(' ')[0]))
                await db.add_order(product_id=int(pro_id['product_id']),
                                   quantity=int(pro_id['quantity']),
                                   user_id=int(pro_id['user_id']),
                                   address_id=int(data.get('select_address')),
                                   payment_type=str(2),
                                   admin_status=str(0),
                                   price=int(pro_id['price']),
                                   pay_type='payme',
                                   _type=pro_id['_type'],
                                   status=True,
                                   a_status=data.get('a_status'),
                                   create_date=datetime.datetime.now())
            await message.answer(pay_success_txt[language],
                                 reply_markup=await get_markup_default_main(btn_txt=main_menu_btn_txt,
                                                                            language=language))

            address = await db.select_address_(id=int(data.get('select_address')))
            distance = get_distance_km(location=(address['latitude'], address['longitude']))

            price = await db.select_dastavka_(qiymat=distance)
            if price is None:
                await message.answer(payme_no_distance[language],
                                     reply_markup=await get_markup_default_main(btn_txt=main_menu_btn_txt,
                                                                                language=language))
                await state.finish()
                return
            else:

                try:

                    address = await db.select_address_(id=int(data.get('select_address')))
                    products = await db.select_user_cart_all_spets(user_id=data.get('user_id'))
                    user = await db.select_user(telegram=message.from_user.id)
                    summa = [int(s['price']) for s in products]

                    str_a = ''
                    product_text = "<b><i>{}</i></b>) <b><i>{}</i></b> - <b><i>{} ({})</i></b> x <b><i>{}</i></b> = <b><i>{}</i></b> {}\n"

                    for _id, product in enumerate(products, 1):
                        p = await db.select_product_single(id=product['product_id'])
                        str_a += product_text.format(_id,
                                                     p['name'],
                                                     product['quantity'],
                                                     product['_type'],
                                                     str(p['price']).split('.')[0],
                                                     "{:,}".format(int(product['quantity']) * int(p['price'])),
                                                     p_type_txt[language])
                    all_summ = "{:,}".format(int(price['price']) + int(sum(summa)))
                    await bot.send_message(chat_id='-1001634768280', text=new_order_text[language].format(
                        datetime.datetime.now().strftime('%Y-%m-%d, %H:%M:%S'),
                        user['fullname'],
                        user['phone'],
                        str_a,
                        "{:,}".format(sum(summa)),
                        'Payme',
                        address['address'],
                        data.get('a_status'),
                        f"{distance:.2f}",
                        "{:,}".format(int(price['price'])),
                        all_summ,
                        status_pay_type_txt[language][0]),
                                           reply_markup=await get_order_admin_markup(succes_btn_txt[language],
                                                                                     user_id=message.from_user.id))

                    geolocator = Nominatim(user_agent="app_name")
                    location = geolocator.reverse(f"{41.324012}, {69.315419}")
                    await bot.send_venue(
                        chat_id='-1001634768280',
                        latitude=address['latitude'],
                        longitude=address['longitude'],
                        title=customer_addres_txt[language].format(user['fullname']),
                        address=location
                    )
                except Exception as e:
                    print("Send message error:", e)

            try:
                await db.delete_user_cart_all(user_id=int(data.get('user_id')))
            except Exception:
                pass

            await state.finish()
        except Exception as e:
            print('Payme Error_2:', e)
