"""
Contact Route — Saves messages from the Contact page into PostgreSQL.
Uses raw SQL to guarantee insertion regardless of ORM table-cache issues.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from database import SessionLocal

router = APIRouter(prefix="/contact", tags=["Contact"])


class ContactForm(BaseModel):
    name:    str
    email:   str
    subject: str = ""
    message: str


def _ensure_table(db):
    """Create contact_messages table if it doesn't exist yet."""
    db.execute(text("""
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
    db.commit()


@router.post("")
def submit_contact(form: ContactForm):
    """Save a contact message using raw SQL — guaranteed to work."""
    name    = (form.name    or "").strip()
    email   = (form.email   or "").strip()
    subject = (form.subject or "").strip()
    message = (form.message or "").strip()

    if not name or not email or not message:
        raise HTTPException(status_code=400, detail="Name, email and message are required.")

    db = SessionLocal()
    try:
        # Ensure table exists (idempotent)
        _ensure_table(db)

        # Insert using raw SQL — no ORM cache issues
        db.execute(text("""
            INSERT INTO contact_messages (name, email, subject, message, is_read)
            VALUES (:name, :email, :subject, :message, FALSE)
        """), {
            "name":    name,
            "email":   email,
            "subject": subject,
            "message": message,
        })
        db.commit()
        print(f"[CONTACT] Saved message from {email} — subject: {subject!r}")
        return {"status": "ok", "message": "Message received. We'll get back to you soon!"}

    except Exception as e:
        db.rollback()
        print(f"[CONTACT ERROR] Failed to save message from {email}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save message. Please try again.")
    finally:
        db.close()


@router.get("/count")
def message_count():
    """Quick health-check endpoint — returns total message count."""
    db = SessionLocal()
    try:
        _ensure_table(db)
        result = db.execute(text("SELECT COUNT(*) FROM contact_messages")).scalar()
        return {"total_messages": result}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()
