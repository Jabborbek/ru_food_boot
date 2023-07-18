from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, bot
from messages.button_text import *
from messages.funcs.get_language import get_language
from messages.funcs.get_markup_default import *
from messages.message_text import *
from states.userstates import AdminFeedback


@dp.callback_query_handler(lambda q: q.data.startswith("feedback_"), state='*')
async def language_query_handler(call: types.CallbackQuery, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    try:
        await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                            reply_markup=await get_markup_inline_feedback(
                                                btn_txt=feedback_pending_btn_txt, language=language,
                                                user_id=call.from_user.id))

        await call.message.answer(feedback_pending_answer_txt[language],
                                  reply_markup=await get_markup_default(language, cancel_btn_txt))

        answer_user_id = call.data.split('_')[1]
        await state.update_data(answer_user_id=answer_user_id, message_id=call.message.message_id)

        await AdminFeedback.answer.set()

    except Exception:
        await call.answer(feedback_error_answer_txt[language])


@dp.message_handler(text=["❌ Bekor qilish", "❌ Отменить"], state=AdminFeedback.answer)
async def get_settings(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = await get_language(types.User.get_current().id)
    try:
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    except Exception as e:
        print(e)
    try:
        await bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=data.get('message_id'),
                                            reply_markup=await get_markup_inline_feedback(
                                                btn_txt=feedback_cancel_btn_txt, language=language,
                                                user_id=message.from_user.id))
    except Exception as e:
        print(e)

    await message.answer(text=cancel_txt[language],
                         reply_markup=await get_markup_default_main(language, main_menu_btn_txt))


@dp.message_handler(content_types='any', state=AdminFeedback.answer)
async def get_settings(message: types.Message, state: FSMContext):
    language = await get_language(types.User.get_current().id)
    data = await state.get_data()
    answer_user_id = data.get('answer_user_id')
    try:
        await bot.send_message(chat_id=answer_user_id, text=feedback_admin_txt[language])
        await bot.copy_message(chat_id=answer_user_id, from_chat_id=message.from_user.id,
                               message_id=message.message_id)
        await message.answer(feedback_success_user_txt[language],
                             reply_markup=await get_markup_default_main(language, main_menu_btn_txt))
        await state.finish()
    except Exception as e:
        print(e)
