from supabase import create_client, Client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if SUPABASE_URL is None or SUPABASE_KEY is None:
    raise ValueError("Supabase URL or Key not found!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def connect():
    """Initialize the database connection (handled by Supabase)."""
    return supabase

def setup_database():
    """Create necessary tables if they don't exist."""
    conn = connect()
    try:
        # Create tables if they do not exist already
        conn.table('messages').upsert([
            {"user_id": 0, "count": 0}
        ], on_conflict=["user_id"]).execute()

        conn.table('statistics').upsert([
            {"user_id": 0, "level": 1, "experience": 0, "coins": 0}
        ], on_conflict=["user_id"]).execute()

        conn.table('prefixes').upsert([
            {"guild_id": 0, "prefix": '!'}
        ], on_conflict=["guild_id"]).execute()

    except Exception as e:
        print(f"Error setting up database: {e}")

def get_messages(user_id):
    """Retrieve the message count for a user."""
    try:
        result = supabase.table('messages').select('count').eq('user_id', user_id).single().execute()
        return result.data['count'] if result.data else 0
    except Exception as e:
        print(f"Error in get_messages: {e}")
        return 0

def set_messages(user_id, count):
    """Set or update the message count for a user."""
    try:
        supabase.table('messages').upsert([
            {"user_id": user_id, "count": count}
        ], on_conflict=["user_id"]).execute()
    except Exception as e:
        print(f"Error in set_messages: {e}")

def get_experience(user_id):
    """Retrieve the experience points of a user."""
    try:
        result = supabase.table('statistics').select('experience').eq('user_id', user_id).single().execute()
        return result.data['experience'] if result.data else 0
    except Exception as e:
        print(f"Error in get_experience: {e}")
        return 0

def set_experience(user_id, exp):
    """Set or update the experience points of a user."""
    try:
        supabase.table('statistics').upsert([
            {"user_id": user_id, "experience": exp}
        ], on_conflict=["user_id"]).execute()
    except Exception as e:
        print(f"Error in set_experience: {e}")

def get_levels(user_id):
    """Retrieve the level of a user."""
    try:
        result = supabase.table('statistics').select('level').eq('user_id', user_id).single().execute()
        return result.data['level'] if result.data else 1
    except Exception as e:
        print(f"Error in get_levels: {e}")
        return 1

def set_levels(user_id, level):
    """Set or update the level of a user."""
    try:
        supabase.table('statistics').upsert([
            {"user_id": user_id, "level": level}
        ], on_conflict=["user_id"]).execute()
    except Exception as e:
        print(f"Error in set_levels: {e}")

def get_coins(user_id):
    """Retrieve the coins of a user."""
    try:
        result = supabase.table('statistics').select('coins').eq('user_id', user_id).single().execute()
        return result.data['coins'] if result.data else 0
    except Exception as e:
        print(f"Error in get_coins: {e}")
        return 0

def set_coins(user_id, coins):
    """Set or update the coins of a user."""
    try:
        supabase.table('statistics').upsert([
            {"user_id": user_id, "coins": coins}
        ], on_conflict=["user_id"]).execute()
    except Exception as e:
        print(f"Error in set_coins: {e}")

def get_all_user_levels():
    """Retrieve levels for all users."""
    try:
        result = supabase.table('statistics').select('user_id, level').execute()
        return {row['user_id']: row['level'] for row in result.data} if result.data else {}
    except Exception as e:
        print(f"Error in get_all_user_levels: {e}")
        return {}

def reset_data():
    """Reset all levels and experience to default values."""
    try:
        supabase.table('statistics').update({"level": 1, "experience": 0, "coins": 0}).execute()
    except Exception as e:
        print(f"Error in reset_data: {e}")

def get_prefix(guild_id):
    """Retrieve the prefix for a specific guild."""
    try:
        result = supabase.table('prefixes').select('prefix').eq('guild_id', guild_id).single().execute()
        return result.data['prefix'] if result.data else "!"
    except Exception as e:
        print(f"Error in get_prefix: {e}")
        return "!"

def set_prefix(guild_id, prefix):
    """Set or update the prefix for a specific guild."""
    try:
        supabase.table('prefixes').upsert([
            {"guild_id": guild_id, "prefix": prefix}
        ], on_conflict=["guild_id"]).execute()
    except Exception as e:
        print(f"Error in set_prefix: {e}")
