import os
from pathlib import Path
from typing import List, Tuple


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
