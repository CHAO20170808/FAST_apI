from locust import HttpUser, task


class User(HttpUser):
    host = "http://localhost:8000"

    @task
    def hello_world(self):
        self.client.get("/home")

    @task
    def get_item(self):
        self.client.get("/item")


    @task
    def get_items(self):
        self.client.get("/all_items")
    # 第 17 行在這裡
