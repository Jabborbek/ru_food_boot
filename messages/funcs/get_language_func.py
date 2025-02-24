from loader import db


async def get_language(user_id):
    user = await db.select_user(telegram=str(user_id))
    if user:
        return user['lang']


from loader import db


async def check_user(user_id):
    if await db.select_user(telegram=int(user_id)) is None:
        return False
    else:
        return True


def check_id(call: str, args: list) -> int:
    for item in args:
        if call in item:
            ports_id = item[call]
            break
    return ports_id
