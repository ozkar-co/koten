from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from koten.api.router import api_router
from koten.core.config import settings
from koten.db.init_db import initialize_database

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


@app.on_event("startup")
def on_startup() -> None:
    initialize_database()
