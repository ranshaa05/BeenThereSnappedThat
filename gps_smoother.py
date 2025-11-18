# -*- coding: utf-8 -*-

"""
Provides GPS track smoothing functionality to correct outliers.
"""

import math
import os

# --- Optional ocean library ---
try:
    from global_land_mask import globe
    HAS_LAND_MASK = True
except ImportError:
    HAS_LAND_MASK = False
    globe = None
    print("Warning: 'global-land-mask' not installed. Ocean glitch correction is disabled.")
    print("To enable, run: pip install global-land-mask")

def haversine(lat1, lon1, lat2, lon2) -> float:
    """Calculates the distance between two GPS coordinates in kilometers."""
    R = 6371  # Earth radius in kilometers
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def smooth_gps_track(
    photos: list,
    speed_enabled: bool = True,
    max_speed_kmh: float = 250.0,
    geo_enabled: bool = True,
    geo_detour_factor: float = 5.0,
    geo_min_direct_km: float = 0.1,
    ocean_enabled: bool = False,
    ocean_max_direct_km: float = 1.0,
    max_passes: int = 5
) -> list:
    """Corrects outliers in a GPS track based on speed, geometry, and land/ocean data."""
    if len(photos) < 3:
        return photos

    corrected_photos = [p.copy() for p in photos]
    total_corrections = 0

    for pass_num in range(1, max_passes + 1):
        corrections_made = 0
        i = 1
        
        while i < len(corrected_photos) - 1:
            prev_p, curr_p, next_p = corrected_photos[i-1:i+2]

            # Calculate time deltas
            dt_total = (next_p['time'] - prev_p['time']).total_seconds()
            dt1 = (curr_p['time'] - prev_p['time']).total_seconds()
            dt2 = (next_p['time'] - curr_p['time']).total_seconds()

            if dt_total <= 1 or dt1 <= 0 or dt2 <= 0:
                i += 1
                continue

            # Calculate distances
            d_total = haversine(prev_p['lat'], prev_p['lon'], next_p['lat'], next_p['lon'])
            d1 = haversine(prev_p['lat'], prev_p['lon'], curr_p['lat'], curr_p['lon'])
            d2 = haversine(curr_p['lat'], curr_p['lon'], next_p['lat'], next_p['lon'])

            # Check for outliers
            reasons = []
            
            if speed_enabled:
                max_speed = max((d1 / dt1) * 3600, (d2 / dt2) * 3600)
                if max_speed > max_speed_kmh:
                    reasons.append(f"speed {max_speed:.0f}km/h")
            
            if geo_enabled and d_total > geo_min_direct_km:
                if (d1 + d2) > (d_total * geo_detour_factor + 1e-6):
                    reasons.append(f"detour>{geo_detour_factor}x")
            
            if ocean_enabled and HAS_LAND_MASK and d_total <= ocean_max_direct_km:
                try:
                    land_status = [globe.is_land(p['lat'], p['lon']) for p in [prev_p, curr_p, next_p]]
                    if not land_status[1] and land_status[0] and land_status[2]:
                        reasons.append("ocean glitch")
                except Exception:
                    pass

            if not reasons:
                i += 1
                continue

            # Interpolate correction
            factor = dt1 / dt_total
            curr_p.update({
                'lat': prev_p['lat'] + factor * (next_p['lat'] - prev_p['lat']),
                'lon': prev_p['lon'] + factor * (next_p['lon'] - prev_p['lon']),
                'corrected': True,
                'corrected_reason': ', '.join(reasons)
            })

            print(f"  [Fix] Pass {pass_num}: Correcting {os.path.basename(curr_p['path'])} ({', '.join(reasons)})")
            corrections_made += 1
            total_corrections += 1
            i += 1

        if not corrections_made:
            break

    if total_corrections:
        print(f"GPS smoothing complete: {total_corrections} correction(s) in {pass_num} pass(es).")
    return corrected_photos
