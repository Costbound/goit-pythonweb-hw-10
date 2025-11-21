from fastapi import FastAPI

from src.api import contacts

app = FastAPI()

app.include_router(contacts.router, prefix="/api", tags=["contacts"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)