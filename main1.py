from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/healthy")
def health_check():
    return {'status': 'Healthy'}    