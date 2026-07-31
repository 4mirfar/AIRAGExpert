from fastapi import FastAPI

from app.api.router import router

app = FastAPI(
    title="AI RAG Expert API",
    version="0.1.0",
)

app.include_router(router)


@app.get("/")
async def root():
    return {
        "message": "AI RAG Expert API is running"
    }