from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# 1. 定義資料模型 (根據第三方服務提供的 JSON 格式)
class WebhookPayload(BaseModel):
    event_type: str
    amount: float
    currency: str
    status: str
    order_id: str

# 2. 模擬金鑰 (實務上應放在環境變數)
WEBHOOK_SECRET = "my_super_secret_token"

@app.post("/webhook")
async def handle_webhook(
    payload: WebhookPayload, 
    x_webhook_token: Optional[str] = Header(None) # 假設對方在 Header 帶入 Token 驗證
):
    # 安全檢查：驗證發送者身分
    if x_webhook_token != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid Token")

    # 處理邏輯
    if payload.event_type == "payment.success":
        print(f"✅ 收到付款！訂單編號: {payload.order_id}, 金額: {payload.amount}")
        # 在這裡執行資料庫更新、發送 Email 等非同步任務
    
    # Webhook 必須快速回傳 200 OK，否則對方可能會判定發送失敗並重複嘗試
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8888)