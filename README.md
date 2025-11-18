# BeenThereSnappedThat

Turn your geotagged photos into interactive trip maps! This tool extracts GPS coordinates and timestamps from your photos to create KMZ files that can be viewed in Google Earth.

## Features

- **Automatic Photo Processing**: Scans folders recursively for geotagged JPEG images
- **GPS Smoothing**: Intelligent correction of GPS errors with multiple methods:
  - Speed outlier correction (fixes impossible speed jumps)
  - Geometric detour correction (removes unnecessary route detours)
  - Ocean glitch correction (fixes coastal road GPS errors)
- **Interactive Configuration**: User-friendly setup with help explanations
- **Google Earth Pro Compatible**: Generates KMZ files with embedded photos and route visualization

## Usage

1. Run the main script:
   ```bash
   python main.py
   ```

2. Select a folder containing your geotagged photos

3. Configure GPS smoothing options:
   - **Speed Outlier Correction**: Recommended for most trips (default: 250 km/h max)
   - **Geometric Detour Correction**: Removes unrealistic route detours
   - **Ocean Glitch Correction**: Fixes GPS points incorrectly placed in water

4. The tool will generate a KMZ file named `trip_YYYY-MM-DD.kmz`

5. Open the KMZ file in Google Earth Pro to view your trip route with photo locations (Google Earth web and MyMaps are not yet supported due to limitations)

## How It Works

1. **Photo Scanning**: Recursively searches for JPEG files with GPS EXIF data
2. **Data Extraction**: Reads GPS coordinates and capture timestamps
3. **GPS Smoothing**: Applies selected correction methods to clean up GPS errors
4. **Route Generation**: Creates a chronological route connecting photo locations
5. **KMZ Creation**: Packages the route and photos into a Google Earth Pro-compatible file

## Supported Formats

- **Input**: JPEG (.jpg, .jpeg) with GPS EXIF data
- **Output**: KMZ files compatible with Google Earth Pro

## Tips

- Ensure your photos have GPS data (most smartphones automatically add this)
- Disable ocean glitch correction if your trip involves taking ferries or boats
- Adjust speed limits based on your trip type (lower for walking/cycling, higher for flights. default is configured for car trips)
