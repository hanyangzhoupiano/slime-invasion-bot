import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL not found!")

def connect():
    """Initialize the database connection."""
    try:
        return psycopg2.connect(DATABASE_URL, sslmode="require")
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def setup_database():
    """Create necessary tables if they don't exist."""
    conn = connect()
    if conn:
        with conn.cursor() as cursor:
            cursor.execute("""
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
            conn.commit()
        conn.close()

def get_messages(user_id):
    """Retrieve the message count for a user."""
    try:
        conn = connect()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT count FROM messages WHERE user_id = %s", (user_id,))
                row = cursor.fetchone()
                return row[0] if row else 0
    except Exception as e:
        print(f"Error in set_messages: {e}")
        conn.rollback()

def set_messages(user_id, count):
    """Set or update the message count for a user."""
    try:
        conn = connect()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO messages (user_id, count) 
                    VALUES (%s, %s) 
                    ON CONFLICT (user_id) 
                    DO UPDATE SET count = EXCLUDED.count
                """, (user_id, count))
                conn.commit()
            conn.close()
    except Exception as e:
        print(f"Error in set_messages: {e}")
        conn.rollback()

def get_experience(user_id):
    """Retrieve the experience points of a user."""
    try:
        conn = connect()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT exp FROM experience WHERE user_id = %s", (user_id,))
                row = cursor.fetchone()
                return row[0] if row else 0
    except Exception as e:
        print(f"Error in set_messages: {e}")
        conn.rollback()

def set_experience(user_id, exp):
    """Set or update the experience points of a user."""
    try:
        conn = connect()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO experience (user_id, exp) 
                    VALUES (%s, %s) 
                    ON CONFLICT (user_id) 
                    DO UPDATE SET exp = EXCLUDED.exp
                """, (user_id, exp))
                conn.commit()
            conn.close()
    except Exception as e:
        print(f"Error in set_messages: {e}")
        conn.rollback()

def get_levels(user_id):
    """Retrieve the level of a user."""
    try:
        conn = connect()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT level FROM experience WHERE user_id = %s", (user_id,))
                row = cursor.fetchone()
                return row[0] if row else 1
    except Exception as e:
        print(f"Error in set_messages: {e}")
        conn.rollback()

def set_levels(user_id, level):
    """Set or update the level of a user."""
    try:
        conn = connect()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO experience (user_id, level) 
                    VALUES (%s, %s) 
                    ON CONFLICT (user_id) 
                    DO UPDATE SET level = EXCLUDED.level
                """, (user_id, level))
                conn.commit()
            conn.close()
    except Exception as e:
        print(f"Error in set_messages: {e}")
        conn.rollback()

def get_all_user_levels():
    """Retrieve levels for all users."""
    try:
        conn = connect()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT user_id, level FROM experience")
                rows = cursor.fetchall()
                return {row[0]: row[1] for row in rows}
    except Exception as e:
        print(f"Error in get_all_user_levels: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

def get_prefix(guild_id):
    """Retrieve the prefix for a specific guild."""
    try:
        conn = connect()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT prefix FROM prefixes WHERE guild_id = %s", (guild_id,))
                row = cursor.fetchone()
                return row[0] if row else "!"
    except Exception as e:
        print(f"Error in set_messages: {e}")
        conn.rollback()

def set_prefix(guild_id, prefix):
    """Set or update the prefix for a specific guild."""
    try:
        conn = connect()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO prefixes (guild_id, prefix) 
                    VALUES (%s, %s) 
                    ON CONFLICT (guild_id) 
                    DO UPDATE SET prefix = EXCLUDED.prefix
                """, (guild_id, prefix))
                conn.commit()
            conn.close()
    except Exception as e:
        print(f"Error in set_messages: {e}")
        conn.rollback()
