# -*- coding: utf-8 -*- 

"""
Generates KML content for the trip.
"""

import html
import os
from image_processing import safe_jpeg_name

def create_kml_content(photos: list, trip_name: str) -> str:
    """Generates the KML content as a string, including a path and photo placemarks."""
    coords = " ".join(f"{p['lon']},{p['lat']},0" for p in photos)
    
    # Build photo placemarks
    placemarks = []
    for i, photo in enumerate(photos):
        jpeg_name = safe_jpeg_name(i + 1)
        img_src = f"images/{jpeg_name}"
        description = f'<![CDATA[<img src="{img_src}" width="800" /><br/>{html.escape(os.path.basename(photo["path"]))}]]>'
        
        placemarks.append(f'''    <Placemark>
      <description>{description}</description>
      <styleUrl>#cameraIcon</styleUrl>
      <Point>
        <coordinates>{photo["lon"]},{photo["lat"]},0</coordinates>
      </Point>
    </Placemark>''')
    
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>{html.escape(trip_name)}</name>
    <Style id="lineStyle">
      <LineStyle>
        <color>ff00aaff</color>
        <width>4</width>
      </LineStyle>
    </Style>
    <Style id="cameraIcon">
      <IconStyle>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/shapes/camera.png</href>
        </Icon>
      </IconStyle>
    </Style>
    <Placemark>
      <name>Trip Path</name>
      <styleUrl>#lineStyle</styleUrl>
      <LineString>
        <coordinates>{coords}</coordinates>
      </LineString>
    </Placemark>
{chr(10).join(placemarks)}
  </Document>
</kml>'''
