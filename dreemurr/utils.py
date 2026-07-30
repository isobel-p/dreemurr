from PIL import Image
import base64
from io import BytesIO

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
