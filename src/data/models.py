from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PasswordEntry(Base):
    __tablename__ = "passwords"

    id = Column(Integer, primary_key=True)
    service = Column(String, nullable=False)
    email = Column(String, nullable=False)
    username = Column(String)
    encrypted_password = Column(String, nullable=False)
    website = Column(String)
    link = Column(String)
    tag = Column(String)
