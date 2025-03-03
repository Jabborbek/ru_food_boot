from aiogram import types
from aiogram.dispatcher import FSMContext

from data.config import ADMINS
from loader import dp, bot
from func_and_message.button_text import *
from func_and_message.funcs.get_language import get_language
from func_and_message.funcs.get_markup_default import get_markup_default, get_markup_default_main, get_markup_inline
from func_and_message.message_text import *
from states.userstates import Feedback


@dp.message_handler(text=["✍️Fikr qoldirish", "✍️Оставить отзыв"], state='*')
async def get_settings(message: types.Message, state: FSMContext):
    await state.finish()
    language = await get_language(types.User.get_current().id)
    await message.answer(text=feedback_txt[language], reply_markup=await get_markup_default(language, cancel_btn_txt))
    await Feedback.step.set()


@dp.message_handler(text=["❌ Bekor qilish", "❌ Отменить"], state=Feedback.step)
async def get_settings(message: types.Message, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    await message.answer(text=cancel_txt[language],
                         reply_markup=await get_markup_default_main(language, main_menu_btn_txt))
    await state.finish()


@dp.message_handler(content_types='any', state=Feedback.step)
async def get_settings(message: types.Message, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    await bot.copy_message(chat_id=ADMINS[0], from_chat_id=message.from_user.id, message_id=message.message_id,
                           reply_markup=await get_markup_inline(language=language, btn_txt=feedback_btn_txt,
                                                                user_id=message.from_user.id, call_text='feedback'))
    await message.answer(text=feedback_success_txt[language],
                         reply_markup=await get_markup_default_main(language, main_menu_btn_txt))
    await state.finish()
