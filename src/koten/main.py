from fastapi import FastAPI

from koten.api.router import api_router
from koten.core.config import settings
from koten.db.init_db import initialize_database

app = FastAPI(title=settings.app_name)
app.include_router(api_router)


@app.on_event("startup")
def on_startup() -> None:
    initialize_database()
