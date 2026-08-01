from PIL import Image
import base64
from io import BytesIO
from pathlib import Path
import re

def encode(path, max_size=1024) -> str:
    with Image.open(path) as img:
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")

        width, height = img.size 
        if width > max_size or height > max_size:
            ratio = min(max_size/width, max_size/height)
            size = (int(width*ratio), int(height*ratio))
            img = img.resize(size, Image.Resampling.LANCZOS)
        
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

def sanitise(name:str) -> str:
    if not name or not name.strip():
        return "unknown"
    clean = re.sub(r'[^\w\-_. ]', '', name)
    clean = clean.replace(" ", "_")
    clean = re.sub(r'_+', '_', clean)
    return clean.strip("_")

def unique(file:Path):
    if not file.exists():
        return file
    stem = file.stem
    suffix = file.suffix
    parent = file.parent
    counter = 1
    while True:
        new = parent / f"{stem}_{counter}{suffix}"
        if not new.exists():
            return new
        counter += 1