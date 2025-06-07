from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

# SQLite DB setup
DATABASE_URL = "sqlite:///./receipts.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ReceiptFile Table - stores metadata of uploaded files
class ReceiptFile(Base):
    __tablename__ = "receipt_file"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String)
    file_path = Column(String)
    is_valid = Column(Boolean, default=False)
    invalid_reason = Column(String, nullable=True)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# Receipt Table - stores extracted information
class Receipt(Base):
    __tablename__ = "receipt"

    id = Column(Integer, primary_key=True, index=True)
    purchased_at = Column(String)
    merchant_name = Column(String)
    total_amount = Column(String)
    file_path = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)
