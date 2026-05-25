# 需要先 pip install websockets
import asyncio
import websockets

async def real_test():
    uri = "ws://127.0.0.1:8080/ws/123"
    async with websockets.connect(uri) as websocket:
        await websocket.send("這是一次真正的網路連線")
        reply = await websocket.recv()
        print(f"從 Server 傳回的真實數據: {reply}")

if __name__ == "__main__":
    asyncio.run(real_test())