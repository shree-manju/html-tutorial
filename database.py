# database.py

from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm.exc import NoResultFound
from datetime import date
import config

# Database setup
DATABASE_URL = "sqlite:///hostel_mess.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define database tables (models)
class Member(Base):
    __tablename__ = "members"
    phone_number = Column(String, primary_key=True, index=True)

class Poll(Base):
    __tablename__ = "polls"
    id = Column(Integer, primary_key=True, index=True)
    poll_date = Column(Date, unique=True)
    is_active = Column(Boolean, default=False)

class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True, index=True)
    poll_id = Column(Integer, ForeignKey("polls.id"))
    member_phone = Column(String, ForeignKey("members.phone_number"))
    selection = Column(String)

# Function to create the database and tables
def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Add members from the config file to the database if they don't exist
    db = SessionLocal()
    try:
        for number in config.MEMBER_PHONE_NUMBERS:
            try:
                db.query(Member).filter(Member.phone_number == number).one()
            except NoResultFound:
                new_member = Member(phone_number=number)
                db.add(new_member)
        db.commit()
    finally:
        db.close()