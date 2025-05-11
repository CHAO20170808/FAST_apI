import logging
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# --- 資料庫設定 ---
DATABASE_URL = "sqlite:///./production.db"
engine = create_engine(DATABASE_URL)

Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    color = Column(String)

Base.metadata.create_all(bind=engine)  # 只在這裡呼叫一次

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pydantic 模型 ---
class ItemSchema(BaseModel):
    name: str
    color: str

    class Config:
        from_attributes = True