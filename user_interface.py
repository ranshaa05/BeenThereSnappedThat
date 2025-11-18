# -*- coding: utf-8 -*-

"""
Handles user interactions, including configuration and file selection.
"""

import tkinter as tk
from tkinter import filedialog
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from gps_smoother import HAS_LAND_MASK

def validate_range(min_val, max_val, type_func=float):
    """Creates a validator for numeric ranges."""
    def validator(value):
        try:
            return min_val <= type_func(value) <= max_val
        except ValueError:
            return False
    return validator

def ask_for_folder() -> str:
    """Opens a dialog to ask the user for a folder."""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder = filedialog.askdirectory(title="Select Folder with Geotagged Photos")
    root.attributes('-topmost', False)
    return folder

def configure_smoothing() -> tuple[bool, float, bool, float, bool, float]:
    """Guides the user through configuring the GPS smoothing options."""
    print("\n" + "=" * 60)
    print("BeenThereSnappedThat - GPS Smoothing".center(60))
    print("=" * 60 + "\n")

    while True:
        choices = [
            Choice("speed", name="Speed Outlier Correction (Recommended)"),
            Choice("geo", name="Geometric Detour Correction"),
        ]

        if HAS_LAND_MASK:
            choices.append(Choice("ocean", name="Ocean Glitch Correction"))
        else:
            choices.append(Choice("ocean", name="Ocean Glitch Correction (library missing)", enabled=False))

        choices += [
            Separator(),
            Choice("help", name="Help: Explain these methods"),
        ]

        selected = inquirer.checkbox(
            message="Select GPS smoothing methods to enable",
            choices=choices,
            default=["speed", "geo"],
            instruction="(Space to toggle, Enter to confirm)",
            transformer=lambda result: f"{len([x for x in result if x != 'help'])} selected" if result else "None",
        ).execute()

        if "help" in selected:
            print("\n" + "-" * 70)
            print("GPS Smoothing Methods Explained".center(70))
            print("-" * 70)
            print("Speed Outlier Correction:")
            print("  - Fixes impossible speed jumps (e.g., in tunnels, cities).")
            print("  - Default max speed is 250 km/h.\n")
            print("Geometric Detour Correction:")
            print("  - Fixes points that create large, unnecessary detours from the main path.\n")
            print("Ocean Glitch Correction:")
            print("  - Fixes points incorrectly placed in the ocean on coastal roads.")
            print("  - Requires 'global-land-mask' library.")
            print("  - Disable for trips involving ferries or boats.\n")
            print("-" * 70)
            input("\nPress Enter to return to selection...")
            continue
        
        break # Exit loop if help was not selected

    speed_enabled = "speed" in selected
    geo_enabled = "geo" in selected
    ocean_enabled = "ocean" in selected and HAS_LAND_MASK

    max_speed_kmh = 250.0
    if speed_enabled:
        max_speed_kmh = inquirer.text(
            message="Maximum speed (km/h):",
            default="250",
            validate=validate_range(50, 1000, int),
            invalid_message="Enter a number between 50 and 1000",
            filter=float,
        ).execute()

    geo_factor = 5.0
    if geo_enabled:
        geo_factor = inquirer.text(
            message="Detour factor (e.g., 5.0 = 5x longer than direct path):",
            default="5.0",
            validate=validate_range(2.0, 20.0),
            invalid_message="Enter a number between 2.0 and 20.0",
            filter=float,
        ).execute()

    ocean_max_direct_km = 1.0
    if ocean_enabled:
        ocean_max_direct_km = inquirer.text(
            message="Max distance for ocean glitch fix (km):",
            default="1.0",
            validate=validate_range(0.1, 10.0),
            invalid_message="Enter a number between 0.1 and 10.0",
            filter=float,
        ).execute()

    print("\n" + "=" * 60)
    print("Configuration complete. Starting processing...".center(60))
    print("=" * 60 + "\n")

    return (speed_enabled, max_speed_kmh, geo_enabled, geo_factor, ocean_enabled, ocean_max_direct_km)
