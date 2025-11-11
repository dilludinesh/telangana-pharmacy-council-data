#!/usr/bin/env python3
"""Initialize SQLite database from JSON data."""
from tgpc.database.sync import sync_json_to_db

if __name__ == "__main__":
    print("🔄 Initializing database from JSON data...")
    print()
    sync_json_to_db()
    print()
    print("✅ Database initialized successfully!")
    print("📁 Location: data/pharmacists.db")
