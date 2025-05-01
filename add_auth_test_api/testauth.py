from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from pydantic import BaseModel

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/demo"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security
SECRET_KEY = "123456"  # 替換成你自己的安全密鑰
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    帳號 = Column(String(255))  # 新增 '帳號' 欄位
    使用者等級 = Column(String(50)) # 新增 使用者等級 欄位
    password =Column(String(255)) # 新增 password 欄位
    items = relationship("Item", back_populates="owner")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(String(255), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")

def create_user(db: Session, user: dict):
    hashed_password = get_password_hash(user["password"])
    db_user = User(username=user["username"], hashed_password=hashed_password, 
                   is_active=True, 帳號=user["username"]
                   ,使用者等級=user["使用者等級"],password=user["password"])  # 假設 '帳號' 欄位的值與 'username' 相同
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Pydantic Models
class UserCreate(BaseModel):
    username: str
    password: str

# Database Utility Functions
def get_db():
    db = SessionLocal()
    try:
        yield db  # 使用 yield 來確保連線關閉
    finally:
        db.close()

def get_session(db: Session = Depends(get_db)):
    return db

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: dict):
    hashed_password = get_password_hash(user["password"])
    db_user = User(username=user["username"], hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = {"username": username}
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data["username"])
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# FastAPI Application
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    print("Database tables created (if not exist).")

# API Endpoints
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    user = get_user(db, form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=dict)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_session)):
    db_user = create_user(db, user.dict())
    return {"username": db_user.username, "id": db_user.id}

@app.get("/users/me", response_model=dict)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return {"id": current_user.id, "username": current_user.username, "is_active": current_user.is_active}

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> dict:
    return {"id": current_user.id, "username": current_user.username, "is_active": current_user.is_active}

@app.get("/users/{user_id}")
async def read_user(user_id: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)) -> dict:
    db_user = get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": db_user.id, "username": db_user.username, "is_active": db_user.is_active}

@app.post("/items/", response_model=dict)
def create_item(item: dict, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    db_item = Item(name=item["name"], description=item.get("description"), owner_id=current_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return {"message": f"Item '{db_item.name}' created successfully!", "id": db_item.id, "owner_id": current_user.id}

@app.get("/items/{item_id}", response_model=dict)
def read_item(item_id: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    db_item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": db_item.id, "name": db_item.name, "description": db_item.description, "owner_id": db_item.owner_id}

@app.put("/items/{item_id}", response_model=dict)
def update_item(item_id: int, item: dict, db: Session = Depends(get_session), current_user: User = Depends(get_current_active_user)):
    db_item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db_item.name = item.get("name", db_item.name)
    db_item.description = item.get("description", db_item.description)
    db.commit()
    db.refresh(db_item)
    return {"message": f"Item '{db_item.name}'  update successfully!", "id": db_item.id, "owner_id": current_user.id}

@app.get("/")
def read_root():
    return {"Hello": "World"}