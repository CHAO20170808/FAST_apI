import pytest
from httpx import ASGITransport, AsyncClient

from database_Old import Item
from main_OLD import app
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.mark.asyncio
async def test_read_main():
    client = AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    )
    response = await client.get("/home")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_read_main_client(test_client):
    response = test_client.get("/home")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

"""
@pytest.mark.integration
def test_client_can_add_read_the_item_from_database(
    test_client, test_db_session
):
    response = test_client.get("/item/1")
    assert response.status_code == 404

    response = test_client.post(
        "/item", json={"name": "ball", "color": "red"}
    )
    assert response.status_code == 201
    # Verify the user was added to the database
    item_id = response.json()
    item = (
        test_db_session.query(Item)
        .filter(Item.id == item_id)
        .first()
    )
    assert item is not None

    response = test_client.get("item/1")
    assert response.status_code == 200
    assert response.json() == {
        "name": "灰",
        "color": "gray",
    }
"""

@pytest.mark.integration
def test_client_can_add_read_the_item_from_database(
    test_client: TestClient, test_db_session: Session
):
    # 先創建一個 item
    item_data_post = {"name": "ball", "color": "red"}
    response_post = test_client.post("/item", json=item_data_post)
    assert response_post.status_code == 201
    item_id = response_post.json()

    # 驗證 item 是否已成功添加到資料庫
    item_from_db = test_db_session.query(Item).filter(Item.id == item_id).first()
    assert item_from_db is not None
    assert item_from_db.name == "ball"
    assert item_from_db.color == "red"

    # 嘗試讀取剛剛創建的 item
    response_get = test_client.get(f"/item/{item_id}")
    assert response_get.status_code == 200
    assert response_get.json() == {"name": "ball", "color": "red"}

    # (可選) 測試讀取一個不存在的 item
    response_not_found = test_client.get("/item/999")
    assert response_not_found.status_code == 404


def test_read(test_client):
    # Create an item first
    item_data_post = {"name": "allen", "color": "qa"}
    response_post = test_client.post("http://127.0.0.1:8000/item", json=item_data_post)
    assert response_post.status_code == 201
    item_id = response_post.json()

    # Now try to read the created item
    response_get = test_client.get(f"http://127.0.0.1:8000/item/{item_id}")
    assert response_get.status_code == 200
    assert response_get.json() == {"name": "allen", "color": "qa"}

    # (Optional) Test trying to read a non-existent item
    response_not_found = test_client.get("http://127.0.0.1:8000/item/999")
    assert response_not_found.status_code == 404