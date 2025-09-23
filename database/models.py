# models.py
from sqlalchemy import Boolean, create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
import os


Base = declarative_base()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "safetyhub.db")
engine = create_engine(f"sqlite:///{db_path}")
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = "users"
    telegram_id = Column(Integer, primary_key=True)
    full_name = Column(String)
    site_id = Column(String)

    audits = relationship("Audit", back_populates="user")


class Audit(Base):
    __tablename__ = "audits"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=True)
    site_id = Column(String, nullable=True)
    title = Column(String, nullable=False)                 # ✅ Add title
    template_path = Column(String, nullable=False)         # ✅ Path to saved JSON
    created_by = Column(String, nullable=False)            # ✅ Telegram ID of admin
    is_active = Column(Boolean, default=False)             # ✅ Whether audit is active
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audits")
    responses = relationship("Response", back_populates="audit")

class Response(Base):
    __tablename__ = "responses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    audit_id = Column(Integer, ForeignKey("audits.id"))
    question_index = Column(Integer)
    category = Column(String)
    question = Column(Text)
    question_ru = Column(String, nullable=True)  
    keyword = Column(String)  
    response = Column(Text)

    audit = relationship("Audit", back_populates="responses")


def init_db():
    Base.metadata.create_all(engine)
