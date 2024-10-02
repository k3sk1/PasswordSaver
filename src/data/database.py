from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base


def get_engine(db_path="passwords.db"):
    return create_engine(f"sqlite:///{db_path}", echo=False)


def create_tables(engine):
    Base.metadata.create_all(engine)


def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
