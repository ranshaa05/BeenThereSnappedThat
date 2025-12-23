# -*- coding: utf-8 -*-

"""
Handles image resizing for the KMZ generator.
"""

import io
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

def safe_webp_name(idx: int) -> str:
    """Generates a safe filename for the image in the KMZ."""
    return f"photo_{idx:04d}.webp"

def resize_to_webp(photo_path: str, idx: int):
    """Resizes an image to fit within 800x600, letterboxing if necessary."""
    try:
        with Image.open(photo_path) as img:
            img = img.convert('RGB')
            w, h = img.size
            scale = min(800 / w, 600 / h)
            new_w, new_h = int(w * scale), int(h * scale)

            # Resize image
            img = img.resize((new_w, new_h), Image.LANCZOS)

            # Create canvas and center image
            canvas = Image.new('RGB', (800, 600), 'white')
            x, y = (800 - new_w) // 2, (600 - new_h) // 2
            canvas.paste(img, (x, y))

            # Save with 70% quality WebP
            buf = io.BytesIO()
            canvas.save(buf, format='WEBP', quality=75, optimize=True, method=6)
            webp_data = buf.getvalue()

            return f"images/{safe_webp_name(idx)}", webp_data

    except Exception as e:
        print(f"  [Error] Could not resize {photo_path}: {e}")
        return None
