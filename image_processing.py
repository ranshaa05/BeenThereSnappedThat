# -*- coding: utf-8 -*-

"""
Handles image resizing for the KMZ generator.
"""

import io
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

def safe_jpeg_name(idx: int) -> str:
    """Generates a safe filename for the image in the KMZ."""
    return f"photo_{idx:04d}.jpg"

def resize_to_jpeg(photo_path: str, idx: int):
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

            # Save with adaptive quality
            buf = io.BytesIO()
            canvas.save(buf, format='JPEG', quality=75, optimize=True, progressive=True)
            jpeg_data = buf.getvalue()
            
            # Re-encode with lower quality if too large
            if len(jpeg_data) > 350 * 1024:
                buf = io.BytesIO()
                canvas.save(buf, format='JPEG', quality=50, optimize=True)
                jpeg_data = buf.getvalue()

            return f"images/{safe_jpeg_name(idx)}", jpeg_data

    except Exception as e:
        print(f"  [Error] Could not resize {photo_path}: {e}")
        return None
