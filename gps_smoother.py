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
    EPS_DIST = 1e-6

    for pass_num in range(1, max_passes + 1):
        this_pass_corrections = 0
        i = 1
        while i < len(corrected_photos) - 1:
            prev_p = corrected_photos[i - 1]
            curr_p = corrected_photos[i]
            next_p = corrected_photos[i + 1]

            dt_total = (next_p['time'] - prev_p['time']).total_seconds()
            dt1 = (curr_p['time'] - prev_p['time']).total_seconds()
            dt2 = (next_p['time'] - curr_p['time']).total_seconds()

            if dt_total <= 1 or dt1 <= 0 or dt2 <= 0:
                i += 1
                continue

            d_total = haversine(prev_p['lat'], prev_p['lon'], next_p['lat'], next_p['lon'])
            d1 = haversine(prev_p['lat'], prev_p['lon'], curr_p['lat'], curr_p['lon'])
            d2 = haversine(curr_p['lat'], curr_p['lon'], next_p['lat'], next_p['lon'])

            speed1 = (d1 / dt1) * 3600
            speed2 = (d2 / dt2) * 3600

            speed_outlier = speed_enabled and (speed1 > max_speed_kmh or speed2 > max_speed_kmh)
            geo_outlier = geo_enabled and ((d1 + d2) > (d_total * geo_detour_factor + EPS_DIST) and d_total > geo_min_direct_km)

            ocean_outlier = False
            if ocean_enabled and HAS_LAND_MASK:
                try:
                    on_land_prev = globe.is_land(prev_p['lat'], prev_p['lon'])
                    on_land_curr = globe.is_land(curr_p['lat'], curr_p['lon'])
                    on_land_next = globe.is_land(next_p['lat'], next_p['lon'])
                    if not on_land_curr and on_land_prev and on_land_next and d_total <= ocean_max_direct_km:
                        ocean_outlier = True
                except Exception:
                    pass

            if not (speed_outlier or geo_outlier or ocean_outlier):
                i += 1
                continue

            # Interpolate a new point
            factor = dt1 / dt_total
            new_lat = prev_p['lat'] + factor * (next_p['lat'] - prev_p['lat'])
            new_lon = prev_p['lon'] + factor * (next_p['lon'] - prev_p['lon'])

            reasons = []
            if speed_outlier: reasons.append(f"speed {max(speed1, speed2):.0f}km/h")
            if geo_outlier: reasons.append(f"detour>{geo_detour_factor}x")
            if ocean_outlier: reasons.append("ocean glitch")

            print(f"  [Fix] Pass {pass_num}: Correcting {os.path.basename(curr_p['path'])} ({', '.join(reasons)})")

            curr_p['lat'] = new_lat
            curr_p['lon'] = new_lon
            curr_p['corrected'] = True
            curr_p['corrected_reason'] = ', '.join(reasons)
            this_pass_corrections += 1
            total_corrections += 1
            i += 1

        if this_pass_corrections == 0:
            break

    if total_corrections > 0:
        print(f"GPS smoothing complete: {total_corrections} correction(s) in {pass_num} pass(es).")
    return corrected_photos
