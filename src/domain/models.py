from sqlalchemy import Integer, String, Date, ForeignKey, Boolean
from db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    hashed_password = mapped_column(String(100), nullable=False)
    avatar = mapped_column(String(255), nullable=True)
    is_confirmed = mapped_column(Boolean, default=False)
    contacts = relationship("Contact", back_populates="owner")


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String, unique=True)
    phone: Mapped[str] = mapped_column(String)
    birthday: Mapped[date] = mapped_column(Date)
    additional_info: Mapped[str] = mapped_column(String, nullable=True)
    owner_id = mapped_column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="contacts")
