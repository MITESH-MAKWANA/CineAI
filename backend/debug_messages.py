"""
Debug script — run locally to check if contact_messages table exists
and has rows in the production PostgreSQL database.
Run with: python debug_messages.py
"""
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    # Try loading .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        DATABASE_URL = os.getenv("DATABASE_URL", "")
    except Exception:
        pass

if not DATABASE_URL:
    print("[ERROR] DATABASE_URL not set. Set it as an environment variable.")
    exit(1)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # 1. Check if table exists
    result = conn.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'contact_messages'
        )
    """))
    exists = result.scalar()
    print(f"contact_messages table exists: {exists}")

    if exists:
        # 2. Count rows
        count = conn.execute(text("SELECT COUNT(*) FROM contact_messages")).scalar()
        print(f"Total messages in DB: {count}")

        # 3. Show latest 5
        rows = conn.execute(text(
            "SELECT id, name, email, subject, message, is_read, created_at "
            "FROM contact_messages ORDER BY created_at DESC LIMIT 5"
        )).fetchall()
        print(f"\nLatest {len(rows)} messages:")
        for r in rows:
            print(f"  ID={r[0]}, name={r[1]}, email={r[2]}, subject={r[3]}, "
                  f"msg={str(r[4])[:40]}, read={r[5]}, at={r[6]}")
    else:
        print("[!] Table does NOT exist — creating it now...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS contact_messages (
                id         SERIAL PRIMARY KEY,
                name       VARCHAR(120) NOT NULL,
                email      VARCHAR(120) NOT NULL,
                subject    VARCHAR(255) DEFAULT '',
                message    TEXT NOT NULL,
                is_read    BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """))
        conn.commit()
        print("[OK] contact_messages table created.")
