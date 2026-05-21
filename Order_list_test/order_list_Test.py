from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import time

app = FastAPI(title="Simple Order Book Server")

# --- 資料結構定義 ---

class Order(BaseModel):
    id: Optional[int] = None
    side: str          # "BUY" 或 "SELL"
    price: float       # 委託價格
    quantity: int      # 委託數量
    timestamp: float = 0.0  # 進入訂單簿的時間（時間優先原則）

class Trade(BaseModel):
    buyer_id: int
    seller_id: int
    price: float
    quantity: int
    timestamp: float

# --- 記憶體內的資料庫 (In-Memory Storage) ---
order_id_counter = 1
# 買單簿：價格從大到小排序 (Desc)
buy_orders: List[Order] = []
# 賣單簿：價格從小到大排序 (Asc)
sell_orders: List[Order] = []
# 成交歷史紀錄
trade_history: List[Trade] = []

# --- 核心撮合邏輯 (Matching Engine) ---

def match_orders():
    """
    核心撮合引擎
    遵循：價格優先（Price Priority）、時間優先（Time Priority）
    """
    global buy_orders, sell_orders, trade_history
    
    # 當買簿最高價 >= 賣簿最低價時，代表有交集，可以持續撮合
    while buy_orders and sell_orders and buy_orders[0].price >= sell_orders[0].price:
        highest_buy = buy_orders[0]  # 目前最高買價
        lowest_sell = sell_orders[0] # 目前最低賣價
        
        # 決定成交價：以「先在訂單簿排隊的那筆訂單」的價格為準（交易所常見做法）
        match_price = highest_buy.price if highest_buy.timestamp < lowest_sell.timestamp else lowest_sell.price
        
        # 決定成交數量：看誰的剩餘張數少，就先吃完誰
        match_quantity = min(highest_buy.quantity, lowest_sell.quantity)
        
        # 紀錄成交
        trade_history.append(Trade(
            buyer_id=highest_buy.id,
            seller_id=lowest_sell.id,
            price=match_price,
            quantity=match_quantity,
            timestamp=time.time()
        ))
        
        # 更新剩餘數量
        highest_buy.quantity -= match_quantity
        lowest_sell.quantity -= match_quantity
        
        # 如果訂單完全成交，移出訂單簿；否則保留
        if highest_buy.quantity == 0:
            buy_orders.pop(0)
        if lowest_sell.quantity == 0:
            sell_orders.pop(0)

# --- API 接口 (Endpoints) ---

@app.post("/order", response_model=Dict[str, str])
def create_order(order: Order):
    global order_id_counter, buy_orders, sell_orders
    
    if order.side.upper() not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail="Side must be 'BUY' or 'SELL'")
    if order.price <= 0 or order.quantity <= 0:
        raise HTTPException(status_code=400, detail="Price and Quantity must be greater than 0")
    
    # 補上系統內部資訊
    order.id = order_id_counter
    order_id_counter += 1
    order.timestamp = time.time()
    order.side = order.side.upper()
    
    # 根據買賣方向，放入對應的訂單簿並排序
    if order.side == "BUY":
        buy_orders.append(order)
        # 買單排序：價格越高越前面(x.price Desc)；價格一樣時，時間越早越前面(x.timestamp Asc)
        buy_orders.sort(key=lambda x: (-x.price, x.timestamp))
    else:
        sell_orders.append(order)
        # 賣單排序：價格越低越前面(x.price Asc)；價格一樣時，時間越早越前面(x.timestamp Asc)
        sell_orders.sort(key=lambda x: (x.price, x.timestamp))
        
    # 每當有新訂單進來，立刻觸發撮合引擎
    match_orders()
    
    return {"status": "success", "message": f"Order {order.id} placed successfully."}

@app.get("/orderbook")
def get_order_book():
    """返回目前的訂單簿狀態"""
    return {
        "buys": [{"id": o.id, "price": o.price, "quantity": o.quantity} for o in buy_orders],
        "sells": [{"id": o.id, "price": o.price, "quantity": o.quantity} for o in sell_orders]
    }

@app.get("/trades", response_model=List[Trade])
def get_trades():
    """返回所有成交歷史"""
    return trade_history


if __name__ == "__main__":
    import uvicorn
    # 啟動伺服器，監聽在 8000 端口
    uvicorn.run(app, host="127.0.0.1", port=8080)