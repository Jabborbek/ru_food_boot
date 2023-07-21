from loader import db


async def check_user(user_id):
    if await db.select_user(telegram=str(user_id)) is None:
        return False
    else:
        return True
