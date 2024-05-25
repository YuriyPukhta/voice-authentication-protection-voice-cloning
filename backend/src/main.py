from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware

from src.api import api_router
from src.api.dependencies.db import init_db
from src.errors import add_error_handlers


def create_app():
    app = FastAPI(
        title="Pre-check-in",
        docs_url="/api/docs",
    )
    app.include_router(api_router, prefix="/api")
    init_db()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    add_error_handlers(app)
    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:create_app", host="127.0.0.1", port=8000)
