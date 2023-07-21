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

    async def add_user(self, id, telegram, created_at, updated_at):
        sql = "INSERT INTO app_user (id, telegram, created_at, updated_at) VALUES($1, $2, $3, $4) returning *"
        return await self.execute(sql, id, telegram, created_at, updated_at, fetchrow=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM app_user WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def select_category(self):
        sql = "SELECT * FROM app_category"
        return await self.execute(sql, fetch=True)

    async def select_subcategory(self):
        sql = "SELECT * FROM app_subcategory"
        return await self.execute(sql, fetch=True)

    async def select_subcategory_where(self, **kwargs):
        sql = "SELECT * FROM app_subcategory WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def select_product(self, **kwargs):
        sql = "SELECT * FROM app_product WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def select_product_single(self, **kwargs):
        sql = "SELECT * FROM app_product WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)
