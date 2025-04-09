from sqlalchemy.orm import Session
from src.domain.models import Contact
from src.schemas import ContactCreate, ContactUpdate


def create_contact(db: Session, contact: ContactCreate, user_id: int):
    existing_contact = db.query(Contact).filter(Contact.email == contact.email).first()
    if existing_contact:
        raise ValueError("A contact with this email already exists.")

    db_contact = Contact(**contact.dict(), owner_id=user_id)
    db.add(db_contact)

    try:
        db.commit()
        db.refresh(db_contact)
        return db_contact
    except Exception as e:
        db.rollback()
        raise ValueError("This email is already used.")


def get_contacts(db: Session, user_id: int, name: str = None, email: str = None):
    query = db.query(Contact).filter(Contact.owner_id == user_id)
    if name:
        query = query.filter((Contact.first_name.ilike(f"%{name}%")) | (Contact.last_name.ilike(f"%{name}%")))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))

    return query.all()


def get_contact(db: Session, contact_id: int, user_id: int):
    return db.query(Contact).filter(Contact.id == contact_id, Contact.owner_id == user_id).first()


def update_contact(db: Session, contact_id: int, contact_update: ContactUpdate, user_id: int):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.owner_id == user_id).first()
    if not contact:
        return None
    for key, value in contact_update.dict(exclude_unset=True).items():
        setattr(contact, key, value)
    db.commit()
    db.refresh(contact)

    return contact


def delete_contact(db: Session, contact_id: int, user_id: int):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.owner_id == user_id).first()
    if contact:
        db.delete(contact)
        db.commit()

    return contact
