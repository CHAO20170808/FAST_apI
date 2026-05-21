import logging

#from sqlalchemy import create_engine
"""
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column
    #sessionmaker,
)
"""


from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, sessionmaker
from typing import List
from sqlalchemy.orm.decl_api import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,mapped_column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String  # 導入這些

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(
        primary_key=True, index=True
    )
    name: Mapped[str] = mapped_column(index=True)
    color: Mapped[str]

"""
DATABASE_URL = "sqlite:///./production.db"


engine = create_engine(DATABASE_URL)

"""
logger.debug("Binding the engine to the database")


#Base.metadata.create_all(bind=engine)

#SessionLocal: sessionmaker[Session] = sessionmaker(
#    autocommit=False, autoflush=False, bind=engine
#)


# --- 資料庫設定 (移至頂部並確保執行) ---
DATABASE_URL = "sqlite:///./production.db"
engine = create_engine(DATABASE_URL)

Base.metadata.create_all(bind=engine)

SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

"""
Base = declarative_base()  # 在 Item 之前定義 Base
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    color = Column(String)
Base.metadata.create_all(bind=engine)  # *明確地* 建立表格

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():  # 已更正的函式名稱
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
        #orm_mode = True
        from_attributes = True

# --- FastAPI 應用程式 ---
#app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/home")
async def read_main():
    return {"message": "Hello World"}

@app.post("/item", response_model=int, status_code=201)
def add_item(item: ItemSchema, db_session: Session = Depends(get_db_session)):
    db_item = Item(name=item.name, color=item.color)
    db_session.add(db_item)
    db_session.commit()
    db_session.refresh(db_item)
    return db_item.id

@app.get("/item/{item_id}", response_model=ItemSchema)
def get_item(item_id: int, db_session: Session = Depends(get_db_session)):
    item_db = db_session.query(Item).filter(Item.id == item_id).first()
    if item_db is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_db

@app.get("/items", response_model=List[ItemSchema])
def get_all_items(db_session: Session = Depends(get_db_session)):
    items_db = db_session.query(Item).all()
    return items_db

"""