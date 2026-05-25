from fastapi import FastAPI, Response
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

app = FastAPI()

@app.get("/rss")
async def get_rss_feed():
    fg = FeedGenerator()
    # 設定 Feed 基本資訊
    fg.title("我的 FastAPI 部落格")
    fg.link(href="https://example.com", rel="alternate")
    fg.description("這是透過 FastAPI 自動產生的 RSS Feed")
    fg.language("zh-TW")

    # 模擬從資料庫抓取的資料
    fake_db = [
        {
            "id": "1",
            "title": "第一篇測試文章",
            "content": "這是內容...",
            "link": "https://example.com/posts/1",
            "date": datetime.now(timezone.utc)
        },
        {
            "id": "2",
            "title": "FastAPI 實作指南",
            "content": "教你如何實作 Feed...",
            "link": "https://example.com/posts/2",
            "date": datetime.now(timezone.utc)
        }
    ]

    # 將資料加入 Feed
    for post in fake_db:
        fe = fg.add_entry()
        fe.id(post["id"])
        fe.title(post["title"])
        fe.link(href=post["link"])
        fe.description(post["content"])
        fe.pubDate(post["date"])

    # 生成 RSS XML 字串
    rss_gen = fg.rss_str(pretty=True)

    # 重點：使用 Response 回傳並指定媒體類型為 application/xml
    return Response(content=rss_gen, media_type="application/xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)