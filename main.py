# -*- coding: utf-8 -*-

"""
BeenThereSnappedThat - Generate KMZ trip maps from geotagged photos.
"""

import os
from pathlib import Path
from tqdm import tqdm
from user_interface import ask_for_folder, configure_smoothing
from exif_utils import get_exif_data, get_capture_time, get_gps_info, standardize_coordinates
from gps_smoother import smooth_gps_track
from kml_generator import create_kml_content
from kmz_creator import save_kmz_file

def main():
    """Main function to run the script."""
    print("\n" + "=" * 60)
    print("BeenThereSnappedThat".center(60))
    print("Turn your geotagged photos into interactive trip maps".center(60))
    print("=" * 60 + "\n")
    
    folder = ask_for_folder()
    if not folder:
        print("No folder selected. Exiting.")
        return

    print("Scanning for geotagged photos...")
    image_files = [str(p) for p in Path(folder).rglob('*') 
                   if p.suffix.lower() in {'.jpg', '.jpeg', '.tif', '.tiff'}]

    photos, invalid_count = [], 0

    for f in tqdm(image_files, desc="Reading EXIF data", unit="img"):
        if not (exif := get_exif_data(f)):
            continue
        
        if not (t := get_capture_time(exif)) or not (gps := get_gps_info(exif)):
            continue
            
        lat, lon = standardize_coordinates(gps)
        if lat is None:
            invalid_count += 1
            continue
            
        photos.append({'path': f, 'time': t, 'lat': lat, 'lon': lon, 'corrected': False, 'corrected_reason': ''})

    if invalid_count:
        print(f"Skipped {invalid_count} images with invalid GPS/time data.")

    if not photos:
        print("No valid geotagged photos found in the selected folder.")
        return

    photos.sort(key=lambda x: x['time'])
    print(f"\nFound {len(photos)} geotagged photos.")

    # Configure and apply GPS smoothing
    speed_enabled, max_speed_kmh, geo_enabled, geo_factor, ocean_enabled, ocean_max_direct_km = configure_smoothing()
    photos = smooth_gps_track(
        photos, speed_enabled, max_speed_kmh, geo_enabled, geo_factor, 
        geo_min_direct_km=0.1, ocean_enabled=ocean_enabled, 
        ocean_max_direct_km=ocean_max_direct_km, max_passes=5
    )

    if not photos:
        print("No valid photos remaining after GPS smoothing.")
        return

    trip_date = photos[0]['time'].strftime('%Y-%m-%d')
    save_path = Path(__file__).parent / f"trip_{trip_date}.kmz"

    kml = create_kml_content(photos, f"BeenThereSnappedThat - {trip_date}")
    save_kmz_file(kml, photos, save_path)

    print("\n" + "=" * 60)
    print("KMZ file created successfully!".center(60))
    print(f"Saved to: {save_path}".center(60))
    print("You can open this file in Google Earth.".center(60))
    print("=" * 60)

if __name__ == "__main__":
    main()
