# -*- coding: utf-8 -*-

"""
Utilities for extracting and processing EXIF and GPS data from images.
"""

from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_exif_data(image_path: str):
    """Extracts raw EXIF data from an image file."""
    try:
        with Image.open(image_path) as img:
            raw = img._getexif()
            if raw is None:
                return None
            return {TAGS.get(k, k): v for k, v in raw.items()}
    except Exception:
        return None

def get_gps_info(exif_data: dict):
    """Extracts GPS info from the raw EXIF data."""
    if exif_data and 'GPSInfo' in exif_data:
        return {GPSTAGS.get(k, k): v for k, v in exif_data['GPSInfo'].items()}
    return None

def _rational_to_float(rational) -> float:
    """Converts a PIL rational number to a float."""
    if isinstance(rational, (list, tuple)) and len(rational) == 2:
        num, den = rational
        return float(num) / float(den) if den != 0 else 0.0
    return float(rational)

def dms_to_decimal(dms, ref: str):
    """Converts Degrees, Minutes, Seconds to decimal coordinates."""
    if not dms or len(dms) != 3:
        return None
    try:
        deg = _rational_to_float(dms[0])
        min_ = _rational_to_float(dms[1])
        sec = _rational_to_float(dms[2])
        decimal = deg + min_ / 60.0 + sec / 3600.0
        ref = ref.strip().upper()
        if ref in ('S', 'W'):
            decimal = -decimal
        return decimal
    except (ValueError, TypeError, IndexError):
        return None

def standardize_coordinates(gps: dict):
    """Extracts and validates latitude and longitude from GPS data."""
    lat = dms_to_decimal(gps.get('GPSLatitude'), gps.get('GPSLatitudeRef', ''))
    lon = dms_to_decimal(gps.get('GPSLongitude'), gps.get('GPSLongitudeRef', ''))
    if lat is None or lon is None or not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return None, None
    if lat == 0.0 and lon == 0.0:
        return None, None
    return lat, lon

def get_capture_time(exif_data: dict) -> datetime | None:
    """Finds the capture time from EXIF data, trying multiple fields."""
    for field in ('DateTimeOriginal', 'DateTimeDigitized', 'DateTime'):
        if field in exif_data:
            try:
                return datetime.strptime(exif_data[field], '%Y:%m:%d %H:%M:%S')
            except (ValueError, TypeError):
                pass
    return None
