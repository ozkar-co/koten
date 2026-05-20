from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from koten.core.config import settings

router = APIRouter(tags=["images"])


def _resolve_image_candidate(filename: str, image_type: str = "full") -> Path:
    """
    Resolve image path, supporting thumbnail variants.
    
    If image_type='thumb', tries to find filename_thumb.jpg, falls back to filename.jpg.
    If image_type='full' (default), serves filename.jpg.
    """
    image_name = Path(filename).name
    if image_name != filename:
        raise HTTPException(status_code=400, detail="Invalid image name")

    base_dir = Path(settings.images_dir)

    # Build candidate path(s) based on type
    requested = Path(image_name)
    suffix = requested.suffix or ".jpg"
    stem = requested.stem
    
    if image_type == "thumb":
        # Try _thumb variant first, fall back to full
        thumb_candidate = base_dir / f"{stem}_thumb{suffix}"
        full_candidate = base_dir / f"{stem}{suffix}"
        
        if thumb_candidate.exists() and thumb_candidate.is_file():
            return thumb_candidate
        elif full_candidate.exists() and full_candidate.is_file():
            return full_candidate
        else:
            raise HTTPException(status_code=404, detail="Image not found")
    else:
        # Serve full image
        if suffix:
            candidate = base_dir / f"{stem}{suffix}"
        else:
            candidate = base_dir / f"{stem}.jpg"
        
        if not candidate.exists() or not candidate.is_file():
            raise HTTPException(status_code=404, detail="Image not found")
        
        return candidate


@router.get("/image/{filename}")
def get_image(filename: str, type: str = "full") -> FileResponse:
    """
    Get an image.
    
    Parameters:
    - filename: image name (e.g., "elfo" or "elfo.jpg")
    - type: "full" (default) or "thumb" (returns thumbnail if available, else full)
    """
    candidate = _resolve_image_candidate(filename, image_type=type)
    return FileResponse(candidate)


@router.get("/image/{filename}/meta")
def get_image_meta(filename: str) -> dict:
    """
    Get metadata for an image, including URLs for both thumbnail and full versions.
    """
    image_name = Path(filename).name
    if image_name != filename:
        raise HTTPException(status_code=400, detail="Invalid image name")

    base_dir = Path(settings.images_dir)
    requested = Path(image_name)
    suffix = requested.suffix or ".jpg"
    stem = requested.stem
    
    full_path = base_dir / f"{stem}{suffix}"
    thumb_path = base_dir / f"{stem}_thumb{suffix}"
    
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    return {
        "name": stem,
        "full": f"/image/{stem}?type=full",
        "thumb": f"/image/{stem}?type=thumb" if thumb_path.exists() else f"/image/{stem}?type=full",
        "has_thumb": thumb_path.exists(),
    }
