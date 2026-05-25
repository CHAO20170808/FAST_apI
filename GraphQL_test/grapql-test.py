import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from typing import List, Optional

# 1. 定義資料模型 (Schema)
@strawberry.type
class Book:
    id: int
    title: str
    author: str

# 模擬資料庫
db_books = [
    Book(id=1, title="The Great Gatsby", author="F. Scott Fitzgerald"),
    Book(id=2, title="1984", author="George Orwell"),
]

# 2. 定義查詢 (Query - Read)
@strawberry.type
class Query:
    @strawberry.field
    def get_books(self) -> List[Book]:
        return db_books

    @strawberry.field
    def get_book(self, id: int) -> Optional[Book]:
        return next((b for b in db_books if b.id == id), None)

# 3. 定義變更 (Mutation - Create, Update, Delete)
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_book(self, title: str, author: str, id: Optional[int] = None) -> Book:
        # 1. 如果有給 id，先檢查會不會跟現有的重複
        if id is not None:
            if any(b.id == id for b in db_books):
                raise Exception(f"ID {id} 已經存在了！")
            new_id = id
        else:
            # 2. 如果沒給 id，自動取最大值 + 1 (避免刪除後 ID 衝突)
            new_id = max([b.id for b in db_books], default=0) + 1
        
        new_book = Book(id=new_id, title=title, author=author)
        db_books.append(new_book)
        return new_book
    
    #def create_book(self, title: str, author: str) -> Book:
       # new_id = len(db_books) + 1
       # new_book = Book(id=new_id, title=title, author=author)
       # db_books.append(new_book)
       # return new_book

    @strawberry.mutation
    def update_book(self, id: int, title: Optional[str] = None, author: Optional[str] = None) -> Optional[Book]:
        for book in db_books:
            if book.id == id:
                if title: book.title = title
                if author: book.author = author
                return book
        return None

    @strawberry.mutation
    def delete_book(self, id: int) -> str:
        global db_books
        db_books = [b for b in db_books if b.id != id]
        return f"Book {id} deleted successfully"

# 4. 建立 Schema 與 FastAPI 路由
schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)