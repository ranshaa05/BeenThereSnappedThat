# -*- coding: utf-8 -*-

"""
Handles the creation of the KMZ file.
"""

import zipfile
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from zipfile import ZipInfo
from image_processing import resize_to_jpeg

def save_kmz_file(kml_content: str, photos: list, save_path: str):
    """Saves KML content and resized images into a single KMZ file."""
    import os
    os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
    print(f"\nCreating KMZ file at: {save_path}")
    
    with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as kmz:
        # Add KML file
        kml_info = ZipInfo('doc.kml', date_time=datetime.now().timetuple())
        kml_info.compress_type = zipfile.ZIP_DEFLATED
        kmz.writestr(kml_info, kml_content)

        # Resize and add images in parallel
        with ThreadPoolExecutor() as executor:
            future_to_photo = {executor.submit(resize_to_jpeg, p['path'], i + 1): p 
                               for i, p in enumerate(photos)}
            
            progress = tqdm(as_completed(future_to_photo), total=len(photos), desc="Resizing images", unit="img")
            
            for future in progress:
                photo_data = future_to_photo[future]
                try:
                    relative_path, jpeg_data = future.result()
                    if relative_path and jpeg_data:
                        img_info = ZipInfo(relative_path, date_time=photo_data['time'].timetuple())
                        img_info.compress_type = zipfile.ZIP_DEFLATED
                        kmz.writestr(img_info, jpeg_data)
                except Exception as e:
                    print(f"Error processing {photo_data['path']}: {e}")
