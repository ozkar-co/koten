from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps

IMAGES_DIR = Path("data/images")
THUMB_SUFFIX = "_thumb"
THUMB_MAX_SIZE = (512, 512)
JPEG_QUALITY = 90
SOURCE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def convert_to_jpg(path: Path) -> Path:
    target = path.with_suffix(".jpg")

    with Image.open(path) as img:
        converted = ImageOps.exif_transpose(img).convert("RGB")
        converted.save(target, format="JPEG", quality=JPEG_QUALITY, optimize=True)

    if path != target and path.exists():
        path.unlink()

    return target


def ensure_thumbnail(jpg_path: Path) -> Path:
    thumb_path = jpg_path.with_name(f"{jpg_path.stem}{THUMB_SUFFIX}.jpg")
    if thumb_path.exists():
        return thumb_path

    with Image.open(jpg_path) as img:
        thumb = ImageOps.exif_transpose(img).convert("RGB")
        thumb.thumbnail(THUMB_MAX_SIZE)
        thumb.save(thumb_path, format="JPEG", quality=JPEG_QUALITY, optimize=True)

    return thumb_path


def is_thumb(path: Path) -> bool:
    return path.stem.endswith(THUMB_SUFFIX)


def process_images(images_dir: Path) -> None:
    images_dir.mkdir(parents=True, exist_ok=True)

    converted_count = 0
    thumb_count = 0

    for path in sorted(images_dir.rglob("*")):
        if not path.is_file():
            continue

        extension = path.suffix.lower()
        if extension not in SOURCE_EXTENSIONS:
            continue

        if is_thumb(path):
            if extension != ".jpg":
                convert_to_jpg(path)
                converted_count += 1
            continue

        jpg_path = path if extension == ".jpg" else convert_to_jpg(path)
        if jpg_path != path:
            converted_count += 1

        thumb_path = jpg_path.with_name(f"{jpg_path.stem}{THUMB_SUFFIX}.jpg")
        if not thumb_path.exists():
            ensure_thumbnail(jpg_path)
            thumb_count += 1

    print(f"Converted to JPG: {converted_count}")
    print(f"Thumbnails created: {thumb_count}")


if __name__ == "__main__":
    process_images(IMAGES_DIR)
