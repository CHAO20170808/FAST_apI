import requests
import pytest

BASE_URL = "http://127.0.0.1:8000"  # 你的 FastAPI 應用程式的基礎 URL

def test_read_item_actual():
    item_id = 4
    url = f"{BASE_URL}/item/{item_id}"
    response = requests.get(url)

    assert response.status_code == 200
    assert response.json() == {"name": "allen", "color": "qa"} # 根據你實際的期望結果調整

def test_create_item_actual():
    url = f"{BASE_URL}/item"
    item_data = {"name": "new item", "color": "blue"}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=item_data, headers=headers)

    assert response.status_code == 201
    item_id = response.json()  # 直接獲取返回的整數 ID
    assert isinstance(item_id, int) # 確保返回的是整數

    # 驗證 item 是否已成功創建
    get_url = f"{BASE_URL}/item/{item_id}"
    get_response = requests.get(get_url)
    assert get_response.status_code == 200
    assert get_response.json() == {"name": "new item", "color": "blue"}

def test_read_nonexistent_item_actual():
    item_id = 999
    url = f"{BASE_URL}/item/{item_id}"
    response = requests.get(url)
    assert response.status_code == 404

def test_delete_item_actual():
    # 確保要刪除的 item 存在
    create_url = f"{BASE_URL}/item"
    item_data = {"name": "new item", "color": "blue"}
    headers = {"Content-Type": "application/json"}
    create_response = requests.post(create_url, json=item_data, headers=headers)
    assert create_response.status_code == 201
    item_to_delete_id = create_response.json()

    # 發送 DELETE 請求
    delete_url = f"{BASE_URL}/item/{item_to_delete_id}"
    delete_response = requests.delete(delete_url)
    assert delete_response.status_code == 204

    # 驗證 item 是否已被刪除
    get_url = f"{BASE_URL}/item/{item_to_delete_id}"
    get_response = requests.get(get_url)
    assert get_response.status_code == 404

    # 測試刪除不存在的 item
    nonexistent_delete_url = f"{BASE_URL}/item/9999"
    nonexistent_delete_response = requests.delete(nonexistent_delete_url)
    assert nonexistent_delete_response.status_code == 404