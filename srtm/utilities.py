from math import sin, cos, radians, atan2, sqrt, ceil
import os
from pathlib import Path
from statistics import mean
from typing import List, Tuple, NamedTuple

EARTH_RADIUS = 6373000
METERS_PER_RADIAN = 6371008


def points_on_line(x1: int, y1: int, x2: int, y2: int) -> List[Tuple[int, int]]:
    # Credit: https://stackoverflow.com/questions/25837544
    points = []
    issteep = abs(y2 - y1) > abs(x2 - x1)
    if issteep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    rev = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        rev = True
    deltax = x2 - x1
    deltay = abs(y2 - y1)
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
    paths = SRTM1_DIR.glob(f"**/{hgt_name}.*")
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


SRTM1_DIR = Path(os.environ.get("SRTM1_DIR", ""))
SRTM3_DIR = Path(os.environ.get("SRTM3_DIR", ""))

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
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return EARTH_RADIUS * c


def apply_curvature(profile_points: List["ElevationProfilePoint"]) -> List["ElevationProfilePoint"]:
    """ Apply the earths curvature to the given heights

    The points given should approximate to a straight line.

    Data is a list of tuples, where each tuple is lat, long, height.

    Data is returned in the same form
    """
    left_size = ceil(len(profile_points) / 2)
    left_points = profile_points[:left_size]
    right_points = profile_points[left_size:]

    # Find our mid-point
    if len(left_points) == len(right_points):
        # We have an equal number of points on both sides, so
        # start in between the two center points
        start_lat = mean((left_points[-1].latitude, right_points[0].latitude))
        start_long = mean((left_points[-1].longitude, right_points[0].longitude))
    else:
        # We have an odd number of heights, so start from the center one
        start_lat = left_points[-1].latitude
        start_long = left_points[-1].longitude

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
    height_deltas = []
    for profile_point in profile_points:
        distance = haversine(start_lat, start_long, profile_point.latitude, profile_point.longitude)
        distance_in_radians = distance / METERS_PER_RADIAN
        earth_drop = EARTH_RADIUS / cos(distance_in_radians) - EARTH_RADIUS
        height_deltas.append(earth_drop)

    # Now we have all our altitudes, subtract each one from the heights we were given,
    # thereby reducing all the heights to account for the curvature of the earth.
    adjusted = []
    for profile_point, height_delta in zip(profile_points, height_deltas):
        adjusted.append(profile_point._replace(elevation=profile_point.elevation - height_delta))

    return adjusted


class StraightLineEquation(NamedTuple):
    gradient: float
    c: float

    def y(self, x):
        return self.gradient * x + self.c

    @classmethod
    def from_points(cls, x1, y1, x2, y2) -> "StraightLineEquation":
        gradient = (y2 - y1) / (x2 - x1)
        c = y1 - (gradient * x1)
        return cls(gradient, c)


class ElevationProfilePoint(NamedTuple):
    latitude: float
    longitude: float
    elevation: float
    distance: float


def get_clearances(
    elevation_profile: List[ElevationProfilePoint],
    start_elevation_offset: float = 0,
    end_elevation_offset: float = 0,
) -> List[float]:
    """Get a list of clearances between the line-of-sight and ground level"""
    start = elevation_profile[0]
    end = elevation_profile[-1]

    if start == end:
        return []

    straight_line = StraightLineEquation.from_points(
        x1=start.distance,
        y1=start.elevation + start_elevation_offset,
        x2=end.distance,
        y2=end.elevation + end_elevation_offset,
    )

    clearances = []
    for point in elevation_profile:
        line_of_sight_elevation = straight_line.y(point.distance)
        clearances.append(line_of_sight_elevation - point.elevation)

    return clearances
