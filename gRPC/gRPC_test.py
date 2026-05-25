import asyncio
import grpc
from fastapi import FastAPI
import uvicorn

# 導入生成的產物
import helloworld_pb2
import helloworld_pb2_grpc

# --- gRPC 伺服器端實作 ---
class Greeter(helloworld_pb2_grpc.GreeterServicer):
    async def SayHello(self, request, context):
        return helloworld_pb2.HelloReply(message=f"你好 {request.name}, 這是來自 gRPC 的問候！")

async def serve_grpc():
    server = grpc.aio.server()
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    print("gRPC Server 啟動於 port 50051...")
    await server.start()
    await server.wait_for_termination()

# --- FastAPI 實作 ---
app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "FastAPI 正常運作中"}

@app.get("/call-grpc/{name}")
async def call_grpc(name: str):
    # FastAPI 作為 Client 呼叫本機的 gRPC 服務
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = helloworld_pb2_grpc.GreeterStub(channel)
        response = await stub.SayHello(helloworld_pb2.HelloRequest(name=name))
    return {"grpc_response": response.message}

# --- 啟動邏輯 ---
async def main():
    # 配置 Uvicorn
    config = uvicorn.Config(app, host="127.0.0.1", port=8080, loop="asyncio")
    uvicorn_server = uvicorn.Server(config)

    # 同時執行 FastAPI 和 gRPC 
    # 注意：在實際生產環境中，通常建議分開部署，或是使用不同的 Process
    await asyncio.gather(
        uvicorn_server.serve(),
        serve_grpc()
    )

if __name__ == "__main__":
    asyncio.run(main())