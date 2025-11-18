# -*- coding: utf-8 -*-

"""
Handles image resizing for the KMZ generator.
"""

import numpy as np
import cv2
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

def safe_jpeg_name(idx: int) -> str:
    """Generates a safe filename for the image in the KMZ."""
    return f"photo_{idx:04d}.jpg"

def resize_to_jpeg(photo_path: str, idx: int):
    """Resizes an image to fit within 800x600, letterboxing if necessary."""
    try:
        img = cv2.imread(photo_path, cv2.IMREAD_COLOR)
        if img is None:
            return None, None

        h, w = img.shape[:2]
        scale = min(800 / w, 600 / h)
        new_w, new_h = int(w * scale), int(h * scale)

        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

        # Create a white canvas and center the image
        canvas = np.full((600, 800, 3), 255, dtype=np.uint8)
        x = (800 - new_w) // 2
        y = (600 - new_h) // 2
        canvas[y:y+new_h, x:x+new_w] = img

        # Encode to JPEG with optimization
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, 75,
                         cv2.IMWRITE_JPEG_OPTIMIZE, 1,
                         cv2.IMWRITE_JPEG_PROGRESSIVE, 1]
        success, buf = cv2.imencode('.jpg', canvas, encode_params)
        if not success:
            return None, None
        jpeg_data = buf.tobytes()

        # If the image is still too large, re-encode with lower quality
        if len(jpeg_data) > 350 * 1024:
            _, buf = cv2.imencode('.jpg', canvas, [cv2.IMWRITE_JPEG_QUALITY, 50])
            jpeg_data = buf.tobytes()

        return f"images/{safe_jpeg_name(idx)}", jpeg_data

    except Exception as e:
        print(f"  [Error] Could not resize {photo_path}: {e}")
        return None, None
