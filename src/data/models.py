from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    failed_attempts = Column(Integer, default=0)
    last_failed_attempt = Column(DateTime, default=None)
    lockout_until = Column(DateTime, default=None)

    # Relasjon til Settings og PasswordEntry
    settings = relationship("Settings", back_populates="user", uselist=False)
    passwords = relationship("PasswordEntry", back_populates="user")


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    theme = Column(String, default="default")
    font_size = Column(Integer, default=12)

    # Relasjon til User
    user = relationship("User", back_populates="settings")


class PasswordEntry(Base):
    __tablename__ = "passwords"

    id = Column(Integer, primary_key=True)
    service = Column(String, nullable=False)
    email = Column(String, nullable=False)
    username = Column(String)
    encrypted_password = Column(String, nullable=False)
    link = Column(String)
    tag = Column(String)

    # Fremmednøkkel til User
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relasjon til User
    user = relationship("User", back_populates="passwords")
