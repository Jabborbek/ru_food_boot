import datetime
from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config


class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    async def add_user(self, fullname, lang, telegram, phone, create_date):
        sql = "INSERT INTO user_user (fullname, lang, telegram, phone, create_date) VALUES($1, $2, $3, $4, $5) returning *"
        return await self.execute(sql, fullname, lang, telegram, phone, create_date, fetchrow=True)

    async def update_user_language(self, lang, telegram):
        sql = "UPDATE user_user SET lang=$1 WHERE telegram=$2"
        return await self.execute(sql, lang, telegram, execute=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM user_user WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def select_user_all(self, **kwargs):
        sql = "SELECT * FROM user_sms WHERE status=True"
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def update_user_fullname(self, fullname, telegram):
        sql = f"UPDATE user_user SET fullname=$1 WHERE telegram=$2"
        return await self.execute(sql, fullname, telegram, execute=True)

    async def update_user_phone(self, phone, telegram):
        sql = f"UPDATE user_user SET phone=$1 WHERE telegram=$2"
        return await self.execute(sql, phone, telegram, execute=True)

    async def add_sms_code(self, user_id, phone, code, status):
        sql = "INSERT INTO user_sms (user_id, phone, code, status) VALUES($1, $2, $3, $4) returning *"
        return await self.execute(sql, user_id, phone, code, status, fetchrow=True)

    async def update_sms_status(self, status, user_id):
        sql = f"UPDATE user_sms SET status=$1 WHERE user_id=$2"
        return await self.execute(sql, status, user_id, execute=True)

    async def update_sms_phone(self, phone, user_id):
        sql = f"UPDATE user_sms SET phone=$1 WHERE user_id=$2"
        return await self.execute(sql, phone, user_id, execute=True)

    async def update_sms_code(self, code, user_id):
        sql = f"UPDATE user_sms SET code=$1, status=False WHERE user_id=$2"
        return await self.execute(sql, code, user_id, execute=True)

    async def select_user_sms_code(self, **kwargs):
        sql = "SELECT * FROM user_sms WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def select_address_all(self, **kwargs):
        sql = "SELECT * FROM user_address WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def select_address_(self, **kwargs):
        sql = "SELECT * FROM user_address WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def add_location(self, address, latitude, longitude, user_id):
        sql = "INSERT INTO user_address (address, latitude, longitude, user_id) VALUES($1, $2, $3, $4) returning *"
        return await self.execute(sql, address, latitude, longitude, user_id, fetchrow=True)

    async def delete_location(self, _id, user_id):
        sql = "DELETE FROM user_address WHERE id=$1 and user_id=$2"
        await self.execute(sql, _id, user_id, execute=True)

    async def delete_location_all(self, user_id):
        sql = "DELETE FROM user_address WHERE user_id=$1"
        await self.execute(sql, user_id, execute=True)

    ###########################################################

    async def delete_tadbir_tree2(self, trening_id, telegram_id):
        sql = "DELETE FROM All_tree where trening_id=$1 and telegram_id=$2"
        await self.execute(sql, trening_id, telegram_id, execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE Users", execute=True)

    """Cart query"""

    async def add_cart(self, user_id, product_id, _type, quantity, price, status, create_date):
        sql = "INSERT INTO user_cart (user_id, product_id, _type, quantity, price, status, create_date) VALUES($1, $2, $3, $4, $5, $6, $7) returning *"
        return await self.execute(sql, user_id, product_id, _type, quantity, price, status, create_date, fetchrow=True)

    async def select_user_cart(self, **kwargs):
        sql = "SELECT * FROM user_cart WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def select_user_cart_all(self, **kwargs):
        sql = "SELECT * FROM user_cart WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def select_user_cart_all_spets(self, user_id):
        sql = "SELECT * FROM user_cart WHERE status=True AND user_id=$1 ORDER BY id ASC"
        return await self.execute(sql, user_id, fetch=True)

    async def update_user_cart(self, quantity, user_id, product_id, _type):
        sql = f"UPDATE user_cart SET quantity=$1 WHERE user_id=$2 AND product_id=$3 AND _type=$4"
        return await self.execute(sql, quantity, user_id, product_id, _type, execute=True)

    async def update_user_cart_with_id(self, quantity, price, user_id, _id):
        sql = f"UPDATE user_cart SET quantity=$1, price=$2 WHERE user_id=$3 AND id=$4"
        return await self.execute(sql, quantity, price, user_id, _id, execute=True)

    async def delete_user_cart(self, _id, user_id):
        sql = "DELETE FROM user_cart WHERE id=$1 AND user_id=$2"
        await self.execute(sql, _id, user_id, execute=True)

    async def delete_user_cart_all(self, user_id):
        sql = "UPDATE user_cart SET status=False WHERE user_id=$1"
        await self.execute(sql, user_id, execute=True)

    async def delete_user_cart_all_del(self, user_id):
        sql = "DELETE FROM user_cart WHERE user_id=$1"
        await self.execute(sql, user_id, execute=True)

    """Product query"""

    async def select_category(self):
        sql = "SELECT * FROM user_category"
        return await self.execute(sql, fetch=True)

    async def select_product(self, **kwargs):
        sql = "SELECT * FROM user_product WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def select_product_single(self, **kwargs):
        sql = "SELECT * FROM user_product WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def select_product_photo(self, **kwargs):
        sql = "SELECT * FROM user_photo WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def select_user_product_measure(self, **kwargs):
        sql = "SELECT * FROM user_product_measure WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def select_user_measure(self, **kwargs):
        sql = "SELECT * FROM user_measure WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def select_user_productquantity(self, **kwargs):
        sql = "SELECT * FROM user_productquantity WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    """Order query"""

    async def add_order(self, product_id, quantity, user_id, address_id, payment_type, admin_status, price, pay_type,
                        _type, status, a_status, create_date):
        sql = "INSERT INTO user_order (product_id, quantity, user_id, address_id, payment_type, admin_status, price, pay_type, _type, status, a_status, create_date) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12) returning *"
        return await self.execute(sql, product_id, quantity, user_id, address_id, payment_type, admin_status, price,
                                  pay_type, _type, status, a_status, create_date, fetchrow=True)

    async def update_user_order_with_id(self, admin_status, user_id):
        sql = f"UPDATE user_order SET admin_status=$1 WHERE user_id=$2"
        return await self.execute(sql, admin_status, user_id, execute=True)

    async def select_user_order_all(self, **kwargs):
        sql = "SELECT * FROM user_order WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def select_user_order_all_sorted(self, user_id):
        sql = "SELECT * FROM user_order WHERE user_id=$1 ORDER BY id ASC"
        return await self.execute(sql, user_id, fetch=True)

    """Admin query"""

    async def select_admin_all(self):
        sql = "SELECT * FROM user_admin"
        return await self.execute(sql, fetch=True)

    """Admin query"""

    async def select_dastavka_(self, qiymat):
        sql = "SELECT * FROM user_dastavka_price WHERE _from <= $1 AND _to >= $1"
        return await self.execute(sql, qiymat, fetchrow=True)
