from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, bot
from messages.button_text import *
from messages.funcs.get_language import get_language
from messages.funcs.get_markup_default import *
from messages.message_text import *


@dp.message_handler(text=["ℹ️Biz haqimizda", "ℹ️О нас"])
async def get_settings(message: types.Message, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    await message.answer(info_txt[language])
