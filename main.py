from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api import auth
from src.api import contacts


app = FastAPI()


app.include_router(contacts.router, prefix="/api", tags=["contacts"])
app.include_router(auth.router, prefix="/api", tags=["auth"])


@app.exception_handler(StarletteHTTPException)
async def custom_404_handler(request, exc):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={"message": "Route not found."},
        )
    # fallback: default handler for other errors
    raise exc


@app.exception_handler(HTTPException)
async def exeption_handler(request, exc):
    if exc.status_code == 500:
        return JSONResponse(
            status_code=500,
            content={"message": "An internal server error occurred."},
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
