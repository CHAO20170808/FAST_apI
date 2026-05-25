import asyncio
import websockets

async def single_client_test(client_id):
    uri = f"ws://127.0.0.1:8080/ws/{client_id}"
    try:
        async with websockets.connect(uri) as websocket:
            message = f"我是編號 {client_id} 的測試員"
            await websocket.send(message)
            
            reply = await websocket.recv()
            print(f"[Client {client_id}] 收到回傳: {reply}")
            
            # 稍微停一下，模擬連線維持了一陣子
            await asyncio.sleep(1) 
            
    except Exception as e:
        print(f"[Client {client_id}] 連線失敗: {e}")

async def main():
    # 建立 10 個不同的任務 (ID 從 1 到 10)
    tasks = []
    for i in range(1, 11):
        tasks.append(single_client_test(i))
    
    # 同時執行所有任務
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    print("開始發起 10 個並行 Socket 連線...")
    asyncio.run(main())
    print("所有測試完成。")