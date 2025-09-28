# models.py
from sqlalchemy import Boolean, create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Index
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
    full_name = Column(String(255), nullable=False)
    site_id = Column(String(50), nullable=False)
    
    # Add indexes for common queries
    __table_args__ = (
        Index('idx_user_site_id', 'site_id'),
        Index('idx_user_full_name', 'full_name'),
    )
    
    audits = relationship("Audit", back_populates="user", cascade="all, delete-orphan")

class Audit(Base):
    __tablename__ = "audits"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.telegram_id"), nullable=False)  # FIXED: Not nullable
    site_id = Column(String(50), nullable=False)  # FIXED: Not nullable
    title = Column(String(255), nullable=False)
    template_path = Column(String(500), nullable=False)
    created_by = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Add indexes for common queries
    __table_args__ = (
        Index('idx_audit_user_id', 'user_id'),
        Index('idx_audit_site_id', 'site_id'),
        Index('idx_audit_timestamp', 'timestamp'),
        Index('idx_audit_active', 'is_active'),
    )
    
    user = relationship("User", back_populates="audits")
    responses = relationship("Response", back_populates="audit", cascade="all, delete-orphan")

class Response(Base):
    __tablename__ = "responses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    audit_id = Column(Integer, ForeignKey("audits.id"), nullable=False)
    question_index = Column(Integer, nullable=False)  # FIXED: Not nullable
    category = Column(String(255), nullable=False)
    question = Column(Text, nullable=False)
    question_ru = Column(Text, nullable=True)
    keyword = Column(String(255), nullable=False)
    response = Column(String(50), nullable=False)  # Constrain response values
    
    # Add indexes for common queries
    __table_args__ = (
        Index('idx_response_audit_id', 'audit_id'),
        Index('idx_response_keyword', 'keyword'),
        Index('idx_response_category', 'category'),
    )
    
    audit = relationship("Audit", back_populates="responses")

def init_db():
    """Initialize database with proper table creation"""
    Base.metadata.create_all(engine)

def get_session():
    """Get a new database session"""
    return Session()

def close_session(session):
    """Safely close database session"""
    try:
        session.close()
    except Exception:
        pass
