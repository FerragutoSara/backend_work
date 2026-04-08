from fastapi import FastAPI
from app.routers.user_router import router as user_router

app = FastAPI(
    title="FastAPI MongoDB Atlas CRUD",
    version="1.0.0"
)

app.include_router(user_router)

@app.get("/")
def root():
    return {"message": "API attiva"}