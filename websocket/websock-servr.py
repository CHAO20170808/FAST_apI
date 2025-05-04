"""
from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print(f"接收到來自客戶端的訊息: {data}")
            response = f"FastAPI 伺服器已接收到你的訊息: {data}"
            await websocket.send_text(response)
    except websockets.exceptions.ConnectionClosedError:
        print("客戶端已斷線")
    except Exception as e:
        print(f"發生錯誤: {e}")
"""


from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect
import websockets

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print(f"接收到來自客戶端的訊息: {data}")
            response = f"FastAPI 伺服器已接收到你的訊息: {data}"
            await websocket.send_text(response)
    except WebSocketDisconnect:
        print("客戶端已正常斷線")
    except websockets.exceptions.ConnectionClosedError:
        print("客戶端已意外斷線 (websockets)")
    except Exception as e:
        print(f"發生錯誤: {e}")