from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import random

app = FastAPI()

# --- 模擬數據 ---
mock_users = {
    "user_123": {"has_drawn": False},
    "test999": {"has_drawn": False} , # 測試帳號
    "test888": {"has_drawn": False}  # 測試帳號
}

class DrawRequest(BaseModel):
    user_id: str

@app.post("/activity/draw")
def do_draw(req: DrawRequest):
    user = mock_users.get(req.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="用戶不存在")

    # --- 關鍵邏輯：針對 test999 的特殊抽獎池 ---
    if req.user_id == "test999":
        # 定義測試獎池：只有 5美元(30%) 和 沒中獎(70%)
        test_prizes = [
            {"label": "恭喜獲得：5美元", "weight": 30, "hit": True},
            {"label": "很遺憾：沒中獎", "weight": 70, "hit": False}
        ]
        
        weights = [p["weight"] for p in test_prizes]
        win_prize = random.choices(test_prizes, weights=weights, k=1)[0]
        
        return {
            "code": 200,
            "user": "test999 (測試模式)",
            "result": win_prize["label"],
            "is_win": win_prize["hit"],
            "note": "此模式僅限 5美元(30%) 與 沒中獎(70%) 的機率測試"
        }


    # --- 關鍵邏輯：針對 test888 的特殊抽獎池 ---
    if req.user_id == "test888":
        # 定義測試獎池：只有 10美元(40%) 和 沒中獎(60%)
        test_prizes = [
            {"label": "恭喜獲得：10美元", "weight": 40, "hit": True},
            {"label": "很遺憾：沒中獎", "weight": 60, "hit": False}
        ]
        
        weights = [p["weight"] for p in test_prizes]
        win_prize = random.choices(test_prizes, weights=weights, k=1)[0]
        
        return {
            "code": 200,
            "user": "test888 (測試模式)",
            "result": win_prize["label"],
            "is_win": win_prize["hit"],
            "note": "此模式僅限 10美元(40%) 與 沒中獎(60%) 的機率測試"
        }



    # --- 一般使用者的邏輯 (會抽到其他獎金，且只能抽一次) ---
    if user["has_drawn"]:
        raise HTTPException(status_code=400, detail="一般用戶只能抽一次")
    
    # 標準獎池
    prizes = [
        {"label": "5美元", "weight": 30},
        {"label": "10美元", "weight": 40},
        {"label": "25美元", "weight": 25},
        {"label": "50美元", "weight": 5}
    ]
    weights = [p["weight"] for p in prizes]
    win_prize = random.choices(prizes, weights=weights, k=1)[0]
    
    user["has_drawn"] = True
    return {"code": 200, "prize": win_prize["label"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)