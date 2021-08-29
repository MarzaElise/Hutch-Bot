"""Absolutely retarded code that is not used anywhere in this repo lmao"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import *

import aiosqlite


class Database(object):
    def __init__(self, db: str):
        r"""
        Database class to provide help with interacting to sqlite3 databases. Will be deleted soon when I move to tortoise :)

        Parameters:
        -----------

        db: `str`

            the database file the connection is going to be made to

        Attributes:
        -----------

        - conn

            - Type: :class:`Optional[aiosqlite.Connect]`

            - Description: the connection that is made. (NoneType when no action was made)

        """
        self.db = db
        self.conn = None

    def __str__(self):
        """Returns the database file the connection is made to"""
        return self.db

    async def get_con(self, db):
        if not self.conn:
            self.conn: aiosqlite.Connection = await aiosqlite.connect(db)
        return self.conn

    async def fetch_all(self, table):
        r"""
        Fetch every piece data from a database,
        ### Not to be used in chat
        """
        self.conn = await self.get_con(self.db)
        async with self.conn.cursor() as cur:
            await cur.execute((f"SELECT * FROM '{table}'"))
            ret: Iterable[aiosqlite.Row] = await cur.fetchall()
        return ret

    async def fetch_all_where(self, table, condition, params: tuple = None):
        r"""Fetch all data from a database where a condition is met"""
        self.conn = await self.get_con(self.db)
        async with self.conn.cursor() as cur:
            await cur.execute(f"SELECT * FROM '{table}' WHERE {condition}", params)
            ret: Iterable[aiosqlite.Row] = await cur.fetchall()
        return ret

    async def fetch_one(self, table, ret, condition, params: tuple = None):
        r"""Fetch one peice of data from a database where a condition is met"""
        self.conn = await self.get_con(self.db)
        async with self.conn.cursor() as cur:
            await cur.execute(f"SELECT {ret} FROM '{table}' WHERE {condition}", params)
            res: aiosqlite.Row = await cur.fetchone()
        return res

    async def execute(self, sql: str, params: tuple = None, *, ret=False):
        r"""Execute a SQL query directly to the DB [returns if there is a `SELECT` statement]"""
        self.conn = await self.get_con(self.db)
        async with self.conn.cursor() as cur:
            await cur.execute(sql, params)
        return None

    async def execute_fetch_all(self, sql, params: tuple = None):
        r"""Execute a query and returns every peice of data. Useful for `SELECT` statements."""
        self.conn = await self.get_con(self.db)
        async with self.conn.cursor() as cur:
            await self.execute(sql, params)
            ret: Iterable[aiosqlite.Row] = await cur.fetchall()
        return ret

    async def fetch(self, one_or_all: str = "all"):
        ret = None
        self.conn = await self.get_con(self.db)
        async with self.conn.cursor() as cur:
            if one_or_all.casefold() == "all":
                ret: Iterable[aiosqlite.Row] = await cur.fetchall()
            else:
                ret: aiosqlite.Row = await cur.fetchone()
        return ret

    async def execute_fetchone(self, sql, params: tuple = None):
        """Execute a SQL query and return a peice of data using `.fetchone`. Useful for `SELECT` statements"""
        self.conn = await self.get_con(self.db)
        async with self.conn.cursor() as cur:
            await self.execute(sql, params)
            ret: aiosqlite.Row = cur.fetchone()
        return ret

    async def get_member_data(self, table, member_id, member_col, required_col=None):
        r"""Get a column value or everything related to a user where the `member_col` is equal to member_id"""
        self.conn = await self.get_con(self.db)
        async with self.conn.cursor() as cur:
            if required_col:
                await cur.execute(
                    f"SELECT {required_col} FROM '{table}' WHERE {member_col} = ?",
                    (member_id,),
                )
                ret: Iterable[aiosqlite.Row] = await cur.fetchall()
                return ret
            else:
                await cur.execute(
                    f"SELECT * FROM '{table}' WHERE {member_col} = ?", (member_id,)
                )
                ret: aiosqlite.Row = await cur.fetchone()
                return ret

    async def update(
        self, table, col_to_update, new_val, condition, params: tuple = None
    ):
        r"""Update a database and set `col_to_update` to `new_val` where a condition is met"""
        self.conn = await self.get_con(self.db)
        async with self.conn.cursor() as cur:
            await cur.execute(
                f"UPDATE '{table}' SET {col_to_update} = {new_val} WHERE {condition}",
                params,
            )
        return None

    async def delete(self, table, condition, params: tuple = None):
        r"""Delete from a database where a condition is met [You are instructed to be careful when using this]"""
        self.conn = await self.get_con(self.db)
        async with self.conn.cursor() as cur:
            await cur.execute(f"DELETE FROM '{table}' WHERE {condition}", params)
        return None

    async def insert(self, table, columns, num_of_cols: int, params: tuple):
        r"""Insert or ignore into a database"""
        self.conn = await self.get_con(self.db)
        to_update = "?," * num_of_cols
        count = list(to_update).count("?")
        if len(params) != count:
            raise TypeError(
                "Amount of {!r}  does not match the amount of parameters".format("?")
            )
        async with self.conn.cursor() as cur:
            await cur.execute(
                f"INSERT OR IGNORE INTO '{table}' ({columns}) VALUES ({to_update})",
                params,
            )
        return None

    async def create(self, table_name, columns: str):
        r"""Create a table named `table_name` and `columns`"""
        self.conn = await self.get_con(self.db)
        async with self.conn.cursor() as cur:
            await cur.execute(
                f"""
                CREATE TABLE IF NOT EXISTS "{table_name}" (
                    {columns}
                );
                """
            )
        return None

    async def select(
        self, table: str, column: str = "*", condition=None, params: tuple = None
    ):
        r"""
        "SELECT" a specific column from `table` where the `Optional[condition]` is met.
        Returns a single or multiple rows based on the column
        """
        # TODO: this is weird, remake it
        self.conn = await self.get_con(self.db)
        async with self.conn.cursor() as cur:
            base = f"SELECT {column} FROM '{table}'"
            if condition:
                base = base + " " + f"WHERE {condition}"
            await cur.execute(base, params)
            if column == "*":
                ret: Iterable[aiosqlite.Row] = await cur.fetchall()
            else:
                ret: aiosqlite.Row = await cur.fetchone()
        return ret


Document = Database
