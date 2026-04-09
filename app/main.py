from fastapi import FastAPI
from app.routers import router as api_router

app = FastAPI(
    title="FastAPI MongoDB Atlas CRUD",
    version="1.0.0",
    root_path="/api"
)

app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "API attiva"}