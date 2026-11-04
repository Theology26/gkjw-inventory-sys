import io
import os
import uuid
from PIL import Image
from fastapi import HTTPException, UploadFile, status
from app.core.config import settings

MAX_IMAGE_DIMENSION = 1280
WEBP_QUALITY = 80
WEBP_METHOD = 4
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}


def compress_and_save_image(
    file: UploadFile,
    subfolder: str,
    custom_filename: str | None = None
) -> str:
    """
    WebP Pipeline as mandated by SKILL.md & AGENTS.md:
    1. Validates image extension.
    2. Opens with Pillow and converts color mode to RGB.
    3. Resizes proportionally using LANCZOS if max dimension > 1280px.
    4. Compresses and writes as .webp (quality=80, method=4) to target folder.
    5. Returns relative path for database storage (e.g. 'photos/items/MAU-005.webp').
    """
    original_filename = file.filename or "upload.jpg"
    _, ext = os.path.splitext(original_filename.lower())

    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Format file tidak didukung ({ext}). Format yang diizinkan: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )

    try:
        content = file.file.read()
        image = Image.open(io.BytesIO(content))

        # Convert palette/RGBA/grayscale to RGB
        if image.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            if image.mode == "P":
                image = image.convert("RGBA")
            background.paste(image, mask=image.split()[-1] if "A" in image.mode else None)
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")

        # Proportional resize if max dimension > 1280px
        width, height = image.size
        max_dim = max(width, height)
        if max_dim > MAX_IMAGE_DIMENSION:
            scale = MAX_IMAGE_DIMENSION / float(max_dim)
            new_width = int(round(width * scale))
            new_height = int(round(height * scale))
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Generate target filename & save
        if custom_filename:
            clean_name = custom_filename if custom_filename.endswith(".webp") else f"{custom_filename}.webp"
        else:
            clean_name = f"{uuid.uuid4().hex[:12]}.webp"

        target_dir = os.path.join(settings.UPLOAD_DIR, subfolder)
        os.makedirs(target_dir, exist_ok=True)

        full_path = os.path.join(target_dir, clean_name)
        image.save(full_path, "WEBP", quality=WEBP_QUALITY, method=WEBP_METHOD)

        # Return relative path for database consistency
        relative_path = os.path.join(subfolder, clean_name).replace("\\", "/")
        return relative_path

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal memproses dan mengompresi gambar: {str(e)}"
        )
    finally:
        file.file.seek(0)

