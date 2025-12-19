"""SQLite database setup"""
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./assessment.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Assessment(Base):
    __tablename__ = "assessments"
    
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Identity
    company_name = Column(String, nullable=False)
    cin = Column(String)
    industry = Column(String, default="restaurant")
    location = Column(String)
    website = Column(String)
    
    # Progress
    current_chapter = Column(Integer, default=1)
    status = Column(String, default="in_progress")
    
    # Scores
    digital_health_score = Column(Float)
    financial_health_score = Column(Float)
    overall_score = Column(Float)
    
    # Contact
    contact_email = Column(String)
    contact_phone = Column(String)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")
