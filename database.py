
import sqlite3
import datetime
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db() -> None:
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                chat_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                approved_at TIMESTAMP
            )
        ''')
        conn.commit()

def add_user(user_id: int, chat_id: int) -> None:
    with get_db_connection() as conn:
        try:
            conn.execute(
                "INSERT INTO users (user_id, chat_id, status, created_at) VALUES (?, ?, ?, ?)",
                (user_id, chat_id, "pending", datetime.datetime.now())
            )
            conn.commit()
        except sqlite3.IntegrityError:
            # User already exists
            pass

def approve_user(user_id: int) -> None:
    with get_db_connection() as conn:
        conn.execute(
            "UPDATE users SET status = ?, approved_at = ? WHERE user_id = ?",
            ("approved", datetime.datetime.now(), user_id)
        )
        conn.commit()

def reject_user(user_id: int) -> None:
    with get_db_connection() as conn:
        conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()

def is_approved(user_id: int) -> bool:
    with get_db_connection() as conn:
        user = conn.execute("SELECT 1 FROM users WHERE user_id = ? AND status = 'approved'", (user_id,)).fetchone()
        return user is not None

def get_all_users() -> list[int]:
    with get_db_connection() as conn:
        users = conn.execute("SELECT user_id FROM users WHERE status = 'approved'").fetchall()
        return [user['user_id'] for user in users]

def is_pending(user_id: int) -> bool:
    with get_db_connection() as conn:
        user = conn.execute("SELECT 1 FROM users WHERE user_id = ? AND status = 'pending'", (user_id,)).fetchone()
        return user is not None

def get_chat_id(user_id: int) -> int | None:
    with get_db_connection() as conn:
        result = conn.execute("SELECT chat_id FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return result['chat_id'] if result else None
