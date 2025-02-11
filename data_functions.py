import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL")

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)

    async def setup(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    user_id BIGINT PRIMARY KEY,
                    count INTEGER DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS experience (
                    user_id BIGINT PRIMARY KEY,
                    level INTEGER DEFAULT 1,
                    exp INTEGER DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS prefixes (
                    guild_id BIGINT PRIMARY KEY,
                    prefix TEXT DEFAULT '!'
                );
            """)

    async def get_messages(self, user_id):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT count FROM messages WHERE user_id = $1", user_id)
            return row["count"] if row else 0

    async def set_messages(self, user_id, count):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO messages (user_id, count) 
                VALUES ($1, $2) 
                ON CONFLICT (user_id) 
                DO UPDATE SET count = $2
            """, user_id, count)

    async def get_experience(self, user_id):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT exp FROM experience WHERE user_id = $1", user_id)
            return row["exp"] if row else 0

    async def set_experience(self, user_id, exp):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO experience (user_id, exp) 
                VALUES ($1, $2) 
                ON CONFLICT (user_id) 
                DO UPDATE SET exp = $2
            """, user_id, exp)

    async def get_levels(self, user_id):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT level FROM experience WHERE user_id = $1", user_id)
            return row["level"] if row else 1

    async def set_levels(self, user_id, level):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO experience (user_id, level) 
                VALUES ($1, $2) 
                ON CONFLICT (user_id) 
                DO UPDATE SET level = $2
            """, user_id, level)

    async def get_prefix(self, guild_id):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT prefix FROM prefixes WHERE guild_id = $1", guild_id)
            return row["prefix"] if row else "!"

    async def set_prefix(self, guild_id, prefix):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO prefixes (guild_id, prefix) 
                VALUES ($1, $2) 
                ON CONFLICT (guild_id) 
                DO UPDATE SET prefix = $2
            """, guild_id, prefix)

db = Database()

async def setup_database():
    await db.connect()
    await db.setup()
