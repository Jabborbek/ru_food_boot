from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp


@dp.message_handler(text='🛠 Поддерживать', state='*')
async def get_category(message: types.Message, state: FSMContext):
    await message.answer(
        text="⚠️ Уважаемый пользователь!\n\nBам тоже нужен сервисный телеграм бот?\n\n🤓 Тогда свяжитесь с нами!"
             "☎️ Контакт: <tg-spoiler><b><i>+998912110399</i></b></tg-spoiler>\n\nАдрес телеграммы: 👉 <tg-spoiler><b><i><a href='https://t.me/Jabborbek_Qobilov'>Admin</a></i></b></tg-spoiler>\n\nЭлектронная почта: 👉 <tg-spoiler>JabborbekQobilov@gmail.com</tg-spoiler>",
        disable_web_page_preview=True
    )
