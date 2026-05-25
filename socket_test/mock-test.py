import fastapi.testclient
# 加上這一行，從你的檔名匯入 app 變數
from socket_tset import app 

client = fastapi.testclient.TestClient(app)

def test_websocket():
    # 使用 client.websocket_connect 建立連接
    with client.websocket_connect("/ws/456") as websocket:
        websocket.send_text("Hello AI")
        data = websocket.receive_text()
        print(f"\n收到回傳: {data}") # 測試時印出來看看
        assert data == "Client #123 說: Hello AI"

# 為了讓你直接執行 python test.py 就能看到結果，加上這兩行
if __name__ == "__main__":
    test_websocket()
    print("測試成功！")