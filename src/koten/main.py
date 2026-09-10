from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.staticfiles import StaticFiles

from koten.api.router import api_router
from koten.core.config import settings
from koten.db.init_db import initialize_database

STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "static"


class SPAStaticFiles(StaticFiles):
    """Serve static assets and fall back to index.html for client-side routes."""

    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404:
                return await super().get_response("index.html", scope)
            raise


app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_origin_regex=settings.cors_allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)
app.mount("/", SPAStaticFiles(directory=str(STATIC_DIR), html=True), name="static")


@app.on_event("startup")
def on_startup() -> None:
    initialize_database()
