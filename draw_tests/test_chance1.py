import requests
import time

URL = "http://127.0.0.1:8001/activity/draw"
TEST_COUNT = 100000
TEST_USER = "test999"

def run_test():
    win_count = 0
    lose_count = 0
    
    # 使用 Session 可以讓速度提升 2~3 倍
    session = requests.Session()
    
    print(f"🚀 開始暴力測試... 預計模擬 {TEST_COUNT:,} 次抽獎")
    start_time = time.time()
    
    for i in range(TEST_COUNT):
        try:
            # 改用 session.post
            response = session.post(URL, json={"user_id": TEST_USER})
            data = response.json()
            
            if data.get("is_win") is True:
                win_count += 1
            else:
                lose_count += 1
                
            # 改成每 1000 次印一次，不然畫面會一直閃，影響速度
            if (i + 1) % 1000 == 0:
                print(f"已完成 {i + 1:,} 次...")
                
        except Exception as e:
            print(f"發生錯誤: {e}")
            break

    end_time = time.time()
    actual_percentage = (win_count / TEST_COUNT) * 100
    
    print("\n" + "="*35)
    print("【機率測試報告 - 10萬次實測】")
    print(f"實際中獎機率: {actual_percentage:.4f}%") # 增加小數點位數看精準度
    print(f"總耗時: {end_time - start_time:.2f} 秒")
    print("="*35)

if __name__ == "__main__":
    run_test()