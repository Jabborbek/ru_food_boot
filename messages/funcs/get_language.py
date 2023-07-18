from loader import db


async def get_language(user_id):
    user = await db.select_user(telegram=user_id)
    if user:
        return user['lang']
