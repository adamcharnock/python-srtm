import math
import os
from pathlib import Path
from statistics import mean
from typing import List, Tuple

EARTH_RADIUS = 6373000
METERS_PER_RADIAN = 6371008

def points_on_line(
    x1: int, y1: int, x2: int, y2: int
) -> List[Tuple[int, int]]:
    # Credit: https://stackoverflow.com/questions/25837544
    points = []
    issteep = abs(y2-y1) > abs(x2-x1)
    if issteep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    rev = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        rev = True
    deltax = x2 - x1
    deltay = abs(y2-y1)
    error = int(deltax / 2)
    y = y1
    ystep = None
    if y1 < y2:
        ystep = 1
    else:
        ystep = -1
    for x in range(x1, x2 + 1):
        if issteep:
            points.append((y, x))
        else:
            points.append((x, y))
        error -= deltay
        if error < 0:
            y += ystep
            error += deltax
    # Reverse the list if the coordinates were reversed
    if rev:
        points.reverse()
    return points


def get_srtm1_file_path(hgt_name: str):
    paths = SRTM1_DIR.glob(f'**/{hgt_name}.*')
    assert (
        paths
    ), f"Path for HGT name {hgt_name} could not be found in {SRTM1_DIR}. Perhaps there is no file for those coordinates?"
    return paths[0]


def get_srtm3_file_path(hgt_name: str):
    for sub_dir in _HGT_SUBDIRS:
        hgt_path = SRTM3_DIR / sub_dir / f"{hgt_name}.hgt.zip"
        if hgt_path.exists():
            return hgt_path
    assert (
        False
    ), f"Path for HGT name {hgt_name} could not be found. Perhaps there is no file for those coordinates?"


SRTM1_DIR = Path(os.environ["SRTM1_DIR"])
SRTM3_DIR = Path(os.environ["SRTM3_DIR"])
_HGT_SUBDIRS = (
    "Eurasia",
    "North_America",
    "Africa",
    "Australia",
    "Islands",
    "South_America",
    "",
)


def haversine(lat1: float, lon1: float, lat2: float, lon2: float):
    """Distance between two lat/long using haversine method"""
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS * c


def apply_curvature(heights: List[Tuple[float, float, int]]):
    """ Apply the earths curvature to the given heights

    The points given should approximate to a straight line.

    Data is a list of tuples, where each tuple is lat, long, height.

    Data is returned in the same form
    """
    left_size = math.ceil(len(heights) / 2)
    left_heights = heights[:left_size]
    right_heights = heights[left_size:]

    # Find our mid-point
    if len(left_heights) == len(right_heights):
        # We have an equal number of points on both sides, so
        # start in beween the two center points
        start_lat = mean((left_heights[-1][0], right_heights[0][0]))
        start_long = mean((left_heights[-1][1], right_heights[0][1]))
    else:
        # We have an odd number of heights, so start from the center one
        start_lat, start_long, _ = left_heights[-1]
    height_deltas = []

    # We we imagine we are walking, and rather then follow the curvature of the
    # earth, we walk out straight on an imaginary plank, seeing the earth slowly
    # fall away below us (because, y'know, it's curved).
    # We then imagine a right angled triangle. The adjacent is the line from
    # our starting position to the center of the earth. The opposite side
    # is the distance we have walked, and the hypotenuse is the distance
    # from our current position to the center of the earth.
    # Given we're now above the earth on our imaginary plank, the hypotenuse
    # should be greater than the earth's radius by however high up we are.
    # If we therefore take away the earths radius, we'll get our altitude.
    for lat, long, _ in heights:
        distance = haversine(start_lat, start_long, lat, long)
        distance_in_radians = distance / METERS_PER_RADIAN
        earth_drop = EARTH_RADIUS/math.cos(distance_in_radians) - EARTH_RADIUS
        height_deltas.append(earth_drop)

    # Now we have all our altitudes, subtract each one from the heights we were given,
    # thereby reducing all the heights to account for the curvature of the earth.
    adjusted = []
    for (latitude, longitude, height), height_delta in zip(heights, height_deltas):
        adjusted.append((latitude, longitude, height - height_delta))

    return adjusted
