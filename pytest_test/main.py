from fastapi import FastAPI, Depends, HTTPException, Request  # 导入 Request
from sqlalchemy.orm import Session
from typing import List
from database import Item, SessionLocal, ItemSchema, get_db_session
from fastapi import FastAPI, Depends, HTTPException, Request # 確保 Request 被導入
from client_logging import client_logger

app = FastAPI()

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

@app.get("/allitems", response_model=List[ItemSchema])
def get_all_items(db_session: Session = Depends(get_db_session)):
    items_db = db_session.query(Item).all()
    return items_db

@app.delete("/item/{item_id}", status_code=204)
def delete_item(item_id: int, db_session: Session = Depends(get_db_session)):
    print(f"Attempting to delete item with ID: {item_id}") # 添加日誌
    item_db = db_session.query(Item).filter(Item.id == item_id).first()
    if item_db is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db_session.delete(item_db)
    db_session.commit()
    print(f"Item with ID: {item_id} deleted successfully.") # 添加日誌
    return  # DELETE 请求通常不返回响应体，只返回状态码

@app.middleware("http")
async def log_requests(request: Request, call_next):
    client_logger.info(
        f"method: {request.method}, "
        f"call: {request.url.path}, "
        f"ip: {request.client.host}"
    )
    response = await call_next(request)
    return response