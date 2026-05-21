import sys
import os

# Get the absolute path to the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
print(f"PROJECT_ROOT: {PROJECT_ROOT}")  # 驗證 PROJECT_ROOT

# Add the project root to the Python path if it's not already there
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)



from main_OLD import app, get_db_session
from database_Old import Base



import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

#from database import Base
#from main import app, get_db_session

#from ..main import app, get_db_session
#from ..database import Base

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

Base.metadata.create_all(bind=engine)  # Create tables

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

@pytest.fixture
def test_db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_client(test_db_session):
    client = TestClient(app)
    app.dependency_overrides[get_db_session] = (
        lambda: test_db_session
    )

    return client
