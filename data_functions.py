import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set. Make sure it is added to the environment variables.")

def connect():
    try:
        return psycopg2.connect(DATABASE_URL, sslmode="require")
    except Exception as e:
        print(f"Database connection error: {e}")
        return None
        
def setup_database():
    conn = connect()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS prefixes (
                    guild_id BIGINT PRIMARY KEY,
                    prefix TEXT NOT NULL
                );
            """)
            conn.commit()
        conn.close()

def get_messages(user_id):
    conn = connect()
    if not conn:
        return 0
    with conn.cursor() as cur:
        cur.execute("SELECT message_count FROM messages WHERE user_id = %s", (user_id,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else 0

def set_messages(user_id, amount):
    conn = connect()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO messages (user_id, message_count) 
                VALUES (%s, %s) 
                ON CONFLICT (user_id) 
                DO UPDATE SET message_count = EXCLUDED.message_count
            """, (user_id, amount))
            conn.commit()
        conn.close()
