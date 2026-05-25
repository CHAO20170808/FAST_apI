from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List
import uvicorn

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        # 儲存活躍連線
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        # 廣播給所有連線
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # 避免單一連線失效導致整個廣播崩潰
                pass

manager = ConnectionManager()

html = """
<!DOCTYPE html>
<html>
    <head><title>FastAPI Chat</title></head>
    <body>
        <h1>FastAPI 即時通訊</h1>
        <h2>你的 ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>傳送</button>
        </form>
        <ul id='messages'></ul>
        <script>
            var client_id = Date.now();
            document.querySelector("#ws-id").textContent = client_id;
            // 注意這裡的 Port 改成跟後端一致的 8080
            var ws = new WebSocket(`ws://localhost:8080/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages');
                var message = document.createElement('li');
                var content = document.createTextNode(event.data);
                message.appendChild(content);
                messages.appendChild(message);
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText");
                ws.send(input.value);
                input.value = '';
                event.preventDefault();
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"用戶 #{client_id} 說: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"用戶 #{client_id} 離開了聊天室")

if __name__ == "__main__":
    # 確保 port 與前端 JavaScript 呼叫的一致
    uvicorn.run(app, host="127.0.0.1", port=8080)