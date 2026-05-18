from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from koten.core.config import settings

router = APIRouter(tags=["images"])


def _resolve_image_candidate(filename: str) -> Path:
    image_name = Path(filename).name
    if image_name != filename:
        raise HTTPException(status_code=400, detail="Invalid image name")

    base_dir = Path(settings.images_dir)

    # Allow extensionless requests by defaulting to .jpg
    requested = Path(image_name)
    if requested.suffix:
        candidate = base_dir / requested.name
    else:
        candidate = base_dir / f"{requested.name}.jpg"

    if not candidate.exists() or not candidate.is_file():
        raise HTTPException(status_code=404, detail="Image not found")

    return candidate


@router.get("/image/{filename}")
def get_image(filename: str) -> FileResponse:
    candidate = _resolve_image_candidate(filename)
    return FileResponse(candidate)
