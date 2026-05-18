from fastapi import APIRouter

from koten.api.images import router as images_router

api_router = APIRouter()
api_router.include_router(images_router)


@api_router.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "koten-backend"}
