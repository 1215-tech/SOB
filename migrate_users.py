
import json
import sqlite3
import datetime
import os

import database

def migrate_users():
    """Migrates users from JSON files to the SQLite database."""
    database.init_db()

    # Migrate approved users
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            try:
                user_ids = json.load(f)
                for user_id in user_ids:
                    try:
                        database.add_user(user_id, 0) # we don't have chat_id for old users
                        database.approve_user(user_id)
                    except Exception as e:
                        print(f"Error migrating approved user {user_id}: {e}")
            except json.JSONDecodeError:
                print("Could not decode users.json")

    # Migrate pending users
    if os.path.exists("pending_users.json"):
        with open("pending_users.json", "r") as f:
            try:
                pending_users = json.load(f)
                for user_id, chat_id in pending_users.items():
                    try:
                        database.add_user(int(user_id), chat_id)
                    except Exception as e:
                        print(f"Error migrating pending user {user_id}: {e}")
            except json.JSONDecodeError:
                print("Could not decode pending_users.json")

    print("User migration completed.")

if __name__ == "__main__":
    migrate_users()
