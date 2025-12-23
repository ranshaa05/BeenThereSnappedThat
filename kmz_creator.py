# -*- coding: utf-8 -*-

"""
Handles the creation of the KMZ file.
"""

import zipfile
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from zipfile import ZipInfo
from image_processing import resize_to_webp

def save_kmz_file(kml_content: str, photos: list, save_path: str):
    """Saves KML content and resized images into a single KMZ file."""
    from pathlib import Path
    
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    print(f"\nCreating KMZ file at: {save_path}")
    
    with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as kmz:
        # Add KML file
        kml_info = ZipInfo('doc.kml', date_time=datetime.now().timetuple())
        kml_info.compress_type = zipfile.ZIP_DEFLATED
        kmz.writestr(kml_info, kml_content)

        # Resize and add images in parallel
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(resize_to_webp, p['path'], i + 1): p 
                      for i, p in enumerate(photos)}
            
            for future in tqdm(as_completed(futures), total=len(photos), desc="Resizing images", unit="img"):
                photo_data = futures[future]
                try:
                    if result := future.result():
                        relative_path, webp_data = result
                        if relative_path and webp_data:
                            img_info = ZipInfo(relative_path, date_time=photo_data['time'].timetuple())
                            img_info.compress_type = zipfile.ZIP_DEFLATED
                            kmz.writestr(img_info, webp_data)
                except Exception as e:
                    print(f"Error processing {photo_data['path']}: {e}")
