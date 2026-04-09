"""
Contact Route — Saves messages from the Contact page into PostgreSQL.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from database import SessionLocal
from models.contact import ContactMessage

router = APIRouter(prefix="/contact", tags=["Contact"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ContactForm(BaseModel):
    name:    str
    email:   str
    subject: str = ""
    message: str


@router.post("")
def submit_contact(form: ContactForm, db: Session = Depends(get_db)):
    msg = ContactMessage(
        name=form.name.strip(),
        email=form.email.strip(),
        subject=form.subject.strip(),
        message=form.message.strip(),
    )
    db.add(msg)
    db.commit()
    return {"status": "ok", "message": "Message received. We'll get back to you soon!"}
