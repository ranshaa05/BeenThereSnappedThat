import sys
import os
import pprint
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime

# Helper functions to process EXIF data (inspired by location_xtractor.py)
def get_exif_data(image_path: str) -> dict | None:
    try:
        with Image.open(image_path) as img:
            raw = img._getexif()
            if raw is None:
                return None
            return {TAGS.get(k, k): v for k, v in raw.items()}
    except Exception:
        return None

def get_capture_time(exif_data: dict) -> datetime | None:
    if not exif_data:
        return None
    for field in ('DateTimeOriginal', 'DateTimeDigitized', 'DateTime'):
        if field in exif_data:
            try:
                return datetime.strptime(exif_data[field], '%Y:%m:%d %H:%M:%S')
            except (ValueError, TypeError):
                continue
    return None

def view_exif(image_path: str, title: str):
    """
    Opens an image and prints its EXIF and GPS metadata under a given title.
    """
    print("\n" + "="*60)
    print(f"--- {title}: {os.path.basename(image_path)}")
    print("="*60)

    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        print(f"Error: File not found at '{image_path}'")
        return
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    raw_exif = img._getexif()
    if not raw_exif:
        print("No EXIF metadata found.")
        return

    exif_data = {TAGS.get(k, k): v for k, v in raw_exif.items()}
    gps_info_raw = exif_data.get('GPSInfo')
    
    print("--- Full EXIF Data ---")
    printable_exif = {}
    for k, v in exif_data.items():
        if isinstance(v, bytes):
            printable_exif[k] = v.decode('utf-8', 'replace')
        else:
            printable_exif[k] = v
    
    pprint.pprint(printable_exif)

    if gps_info_raw:
        gps_info = {GPSTAGS.get(k, k): v for k, v in gps_info_raw.items()}
        print("\n--- Decoded GPS Info ---")
        pprint.pprint(gps_info)
    else:
        print("\n--- No GPS Info Found ---")


def main(target_path: str):
    """
    Finds and inspects the target image and its chronological neighbors.
    """
    target_path = os.path.abspath(target_path)
    if not os.path.exists(target_path):
        print(f"Error: Target file does not exist: {target_path}")
        return

    folder = os.path.dirname(target_path)
    print(f"Scanning for images in: {folder}")

    image_exts = {'.jpg', '.jpeg', '.tiff', '.tif'}
    all_photos = []

    for f in os.listdir(folder):
        path = os.path.join(folder, f)
        if os.path.splitext(f)[1].lower() in image_exts:
            exif = get_exif_data(path)
            time = get_capture_time(exif)
            if time:
                all_photos.append({'path': path, 'time': time})

    if not all_photos:
        print("No images with valid capture times found in the directory.")
        return

    all_photos.sort(key=lambda x: x['time'])

    target_index = -1
    for i, photo in enumerate(all_photos):
        if os.path.samefile(photo['path'], target_path):
            target_index = i
            break
    
    if target_index == -1:
        print("Could not find the target image in the list of photos with valid time data.")
        print("Showing EXIF for target file directly:")
        view_exif(target_path, "Target Image (Direct Read)")
        return

    print(f"\nFound {len(all_photos)} images. Target is at position {target_index + 1}.")

    # Define the window of photos to inspect
    indices_to_inspect = {
        -2: "Neighbor -2",
        -1: "Neighbor -1",
        0: "Target Image",
        1: "Neighbor +1",
        2: "Neighbor +2"
    }

    for offset, title in indices_to_inspect.items():
        index = target_index + offset
        if 0 <= index < len(all_photos):
            view_exif(all_photos[index]['path'], title)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python exif_viewer.py \"<path_to_your_image>\"")
    else:
        main(sys.argv[1])
