from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from data.config import ADMINS
from loader import db


class is_admin(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        if message.from_user.id in [int(i['telegram']) for i in await db.select_admin_all()]:
            return True
        else:
            return False
