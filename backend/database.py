from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./complaints.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(255), nullable=False)
    product_name = Column(String(255), nullable=True)
    batch_number = Column(String(100), nullable=True)
    
    country = Column(String(100), nullable=True)
    quantity_affected = Column(String(100), nullable=True)
    complaint_text = Column(Text, nullable=False)
    attachment_filename = Column(String(500), nullable=True)

    is_complete = Column(Boolean, default=False)
    missing_fields = Column(Text, nullable=True)
    risk_level = Column(String(20), nullable=True)
    risk_reasoning = Column(Text, nullable=True)

    status = Column(String(50), default="Open")
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
