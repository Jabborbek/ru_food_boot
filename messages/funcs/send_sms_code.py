import random
from loader import db, bot
import requests as requests

from messages.message_text import confirm_smm_code_txt, error_phone_number_txt


async def send_sms_code(phone: str, lang: str, user_id, telegram):
    code = "".join([str(random.randint(0, 100) % 10) for _ in range(6)])
    user = await db.select_user_sms_code(user_id=int(user_id))
    print(f'{code=}')
    if user is None:
        await db.add_sms_code(
            user_id=int(user_id),
            phone=int(phone),
            code=str(code),
            status=False
        )
    else:
        await db.update_sms_code(code=str(code), user_id=int(user_id))
    abonent_code = phone[3:5]

    if int(abonent_code) in [97, 88]:
        try:
            return requests.get(
                f"https://portal.inhub.uz:8443/bq?sn=6300&msisdn={phone}&message={confirm_smm_code_txt[lang].format(code)}")
        except Exception as e:
            print(e)
    elif int(abonent_code) in [90, 91]:
        try:
            return requests.get(
                f"https://portal.inhub.uz:8443/bq?sn=bystars&msisdn={phone}&message={confirm_smm_code_txt[lang].format(code)}")
        except Exception as e:
            print(e)
    elif int(abonent_code) in [99, 77, 95, 93, 94, 98, 33]:
        try:
            return requests.get(
                f"https://portal.inhub.uz:8443/bq?sn=6500&msisdn={phone}&message={confirm_smm_code_txt[lang].format(code)}")
        except Exception as e:
            print(e)
    else:
        return await bot.send_message(chat_id=telegram, text=error_phone_number_txt[lang])
