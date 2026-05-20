from fastapi import APIRouter

from koten.api.images import router as images_router
from koten.api.lexicon import router as lexicon_router
from koten.api.lore import router as lore_router
from koten.api.symbols import router as symbols_router

api_router = APIRouter()
api_router.include_router(images_router)
api_router.include_router(lexicon_router)
api_router.include_router(lore_router)
api_router.include_router(symbols_router)


@api_router.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "koten-backend"}
