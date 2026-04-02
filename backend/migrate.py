"""
One-time migration to add new columns to the users table.
Run: python migrate.py
"""
import sqlite3

DB_PATH = "cineai.db"

def run():
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    existing = [row[1] for row in cur.execute("PRAGMA table_info(users)").fetchall()]
    print("Existing columns:", existing)

    migrations = [
        ("skipped_genres",  "TEXT NOT NULL DEFAULT ''"),
        ("age",             "INTEGER"),
        ("gender",          "TEXT NOT NULL DEFAULT ''"),
        ("onboarding_done", "INTEGER NOT NULL DEFAULT 0"),
    ]

    for col, typedef in migrations:
        if col not in existing:
            sql = f"ALTER TABLE users ADD COLUMN {col} {typedef}"
            cur.execute(sql)
            print(f"  + Added column: {col}")
        else:
            print(f"  ~ Already exists: {col}")

    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    run()
