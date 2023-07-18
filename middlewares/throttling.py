import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled

from messages.funcs.get_language import get_language
from messages.message_text import not_working_sunday_txt, not_working_time_not_saturday_txt

LOG_FILE = 'error.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)


class ThrottlingMiddleware(BaseMiddleware):
    """
    Simple middleware
    """

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        current_time = message.date.strftime("%H:%M")
        if message.date.weekday() == 6:
            await self.message_answer_user_sunday(message)
            raise CancelHandler()

        if current_time < "09:00" or current_time > "19:00":
            await self.message_answer_user(message)
            raise CancelHandler()

        else:
            handler = current_handler.get()
            dispatcher = Dispatcher.get_current()
            if handler:
                limit = getattr(handler, "throttling_rate_limit", self.rate_limit)
                key = getattr(handler, "throttling_key", f"{self.prefix}_{handler.__name__}")
            else:
                limit = self.rate_limit
                key = f"{self.prefix}_message"
            try:
                await dispatcher.throttle(key, rate=limit)
            except Throttled as t:
                await self.message_throttled(message, t)
                raise CancelHandler()

    async def message_throttled(self, message: types.Message, throttled: Throttled):
        if throttled.exceeded_count <= 2:
            await message.reply("Too many requests!")

    async def message_answer_user(self, message: types.Message):
        language = await get_language(message.from_user.id)
        try:
            await message.answer(not_working_time_not_saturday_txt[language], reply_markup=types.ReplyKeyboardRemove())
        except Exception as e:
            logging.info(f"Not working time error: {e}")

    async def message_answer_user_sunday(self, message: types.Message):
        language = await get_language(message.from_user.id)
        try:
            await message.answer(not_working_sunday_txt[language], reply_markup=types.ReplyKeyboardRemove())
        except Exception as e:
            logging.info(f"Not working sunday error: {e}")
