import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL")

pool = None  # Global connection pool

async def connect_db():
    """Initialize the database connection pool."""
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)

await connect_db()

async def setup_database():
    """Create necessary tables if they don't exist."""
    async with pool.acquire() as conn:
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

async def get_messages(user_id):
    """Retrieve the message count for a user."""
    if pool is None:
        return
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT count FROM messages WHERE user_id = $1", user_id)
        return row["count"] if row else 0

async def set_messages(user_id, count):
    """Set or update the message count for a user."""
    if pool is None:
        return
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO messages (user_id, count) 
            VALUES ($1, $2) 
            ON CONFLICT (user_id) 
            DO UPDATE SET count = EXCLUDED.count
        """, user_id, count)

async def get_experience(user_id):
    """Retrieve the experience points of a user."""
    if pool is None:
        return
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT exp FROM experience WHERE user_id = $1", user_id)
        return row["exp"] if row else 0

async def set_experience(user_id, exp):
    """Set or update the experience points of a user."""
    if pool is None:
        return
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO experience (user_id, exp) 
            VALUES ($1, $2) 
            ON CONFLICT (user_id) 
            DO UPDATE SET exp = EXCLUDED.exp
        """, user_id, exp)

async def get_levels(user_id):
    """Retrieve the level of a user."""
    if pool is None:
        return
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT level FROM experience WHERE user_id = $1", user_id)
        return row["level"] if row else 1

async def set_levels(user_id, level):
    """Set or update the level of a user."""
    if pool is None:
        return
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO experience (user_id, level) 
            VALUES ($1, $2) 
            ON CONFLICT (user_id) 
            DO UPDATE SET level = EXCLUDED.level
        """, user_id, level)

async def get_prefix(guild_id):
    """Retrieve the prefix for a specific guild."""
    if pool is None:
        return
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT prefix FROM prefixes WHERE guild_id = $1", guild_id)
        return row["prefix"] if row else "!"

async def set_prefix(guild_id, prefix):
    """Set or update the prefix for a specific guild."""
    if pool is None:
        return
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO prefixes (guild_id, prefix) 
            VALUES ($1, $2) 
            ON CONFLICT (guild_id) 
            DO UPDATE SET prefix = EXCLUDED.prefix
        """, guild_id, prefix)
