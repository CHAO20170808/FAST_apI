from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/demo"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(String(255), nullable=True)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    print("Database tables created (if not exist).")

@app.get("/items/")
def read_items(db: Session = Depends(get_db)):
    items = db.query(Item).all()
    return items

@app.post("/items/", response_model=dict)
def create_item(item: dict, db: Session = Depends(get_db)):
    db_item = Item(name=item["name"], description=item.get("description"))
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return {"message": f"Item '{db_item.name}' created successfully!"}

@app.get("/items/{item_id}", response_model=dict)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": db_item.id, "name": db_item.name, "description": db_item.description}

@app.put("/items/{item_id}", response_model=dict)
def update_item(item_id: int, item: dict, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db_item.name = item.get("name", db_item.name)
    db_item.description = item.get("description", db_item.description)
    db.commit()
    db.refresh(db_item)
    return {"message": f"Item '{db_item.name}' updated successfully!", "id": db_item.id}

@app.delete("/items/{item_id}", response_model=dict)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": f"Item with id '{item_id}' deleted successfully!"}


@app.get("/")
def read_root():
    return {"Hello": "World"}