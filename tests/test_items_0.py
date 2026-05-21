from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main_OLD import app, get_db_session  # 直接導入
from database_Old import Item  # 直接導入

def test_create_and_read_item(test_client: TestClient, test_db_session: Session):
    item_data = {"name": "Test Item", "color": "red"}
    response = test_client.post("/item", json=item_data)
    assert response.status_code == 201
    item_id = response.json()

    response = test_client.get(f"/item/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["color"] == "red"