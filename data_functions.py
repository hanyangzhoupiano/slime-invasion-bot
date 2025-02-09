import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")

def connect():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def setup_database():
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    user_id BIGINT PRIMARY KEY,
                    message_count INT DEFAULT 0
                )
            """)
            conn.commit()

def get_messages(user_id):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT message_count FROM messages WHERE user_id = %s", (user_id,))
            row = cur.fetchone()
            return row[0] if row else 0

def set_messages(user_id, amount):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO messages (user_id, message_count) 
                VALUES (%s, 1) 
                ON CONFLICT (user_id) 
                DO UPDATE SET message_count = amount
            """, (user_id,))
            conn.commit()
