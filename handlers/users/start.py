import datetime
import uuid

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart

from keyboards.default.main_kb import main_menu_kb
from loader import dp, db
from messages.funcs.check_user import check_user


@dp.message_handler(CommandStart(), chat_type='private', state='*')
async def bot_start(message: types.Message, state: FSMContext):
    await state.finish()
    if await check_user(user_id=message.from_user.id):
        await message.answer(
            text='Привет и добро пожаловать!',
            reply_markup=main_menu_kb
        )
    else:
        await db.add_user(telegram=str(message.from_user.id),
                          id=uuid.uuid4(),
                          updated_at=datetime.datetime.now(),
                          created_at=datetime.datetime.now())

        await message.answer(
            text='Привет и добро пожаловать!',
            reply_markup=main_menu_kb
        )
