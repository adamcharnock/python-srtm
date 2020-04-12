# Attempt 2
import math
import os
from pathlib import Path
from typing import NamedTuple, Dict, Tuple, Generator
from zipfile import ZipFile

HGT_DIR = Path(os.environ["SRTM_DIR"])
_HGT_SUBDIRS = (
    "Eurasia",
    "North_America",
    "Africa",
    "Australia",
    "Islands",
    "South_America",
    "",
)


def get_hgt_path(hgt_name: str):
    for sub_dir in _HGT_SUBDIRS:
        hgt_path = HGT_DIR / sub_dir / f"{hgt_name}.hgt.zip"
        if hgt_path.exists():
            return hgt_path
    assert (
        False
    ), f"Path for HGT name {hgt_name} could not be found. Perhaps there is no file for those coordinates?"


class RasterBaseCoordinates(NamedTuple):
    latitude: int
    longitude: int

    @classmethod
    def from_float(cls, latitude: float, longitude: float):
        # Raster base coordinates are measured from the bottom left (i.e SE)
        # corner. So we need calculate the base coordate a bit differently for
        # negative lat/longs.
        if latitude < 0:
            latitude -= 1
        if longitude < 0:
            longitude -= 1

        return cls(latitude=int(latitude), longitude=int(longitude))

    @classmethod
    def from_hgt_name(cls, hgt_name: str):
        hgt_name = hgt_name.upper()
        error = f"Invalid hgt name ({hgt_name}), expected format (N|S)00(E|W)000"
        assert len(hgt_name) == 7, error
        assert hgt_name[0] in ("N", "S"), error
        assert hgt_name[3] in ("E", "W"), error
        try:
            is_north = hgt_name[0] == "N"
            latitude = int(hgt_name[1:3])
            is_east = hgt_name[3] == "E"
            longitude = int(hgt_name[4:7])
        except ValueError:
            assert False, error

        if not is_north:
            latitude *= -1
        if not is_east:
            longitude *= -1

        return cls(latitude=latitude, longitude=longitude)

    @classmethod
    def from_hgt_path(cls, path: Path):
        return cls.from_hgt_name(hgt_name=path.name.split(".")[0])

    @property
    def hgt_name(self):
        if self.latitude >= 0:
            latitude = f"N{self.latitude:0>2}"
        else:
            latitude = f"S{-self.latitude:0>2}"

        if self.longitude >= 0:
            longitude = f"E{self.longitude:0>3}"
        else:
            longitude = f"W{-self.longitude:0>3}"

        return f"{latitude}{longitude}"


class HeightMap:
    raster: bytes = None
    base_coordinates: RasterBaseCoordinates
    expected_values = 1442401
    values_per_row = 1201

    def __init__(self, path: Path, base_coordinates: RasterBaseCoordinates = None):
        self.path = path
        self.base_coordinates = base_coordinates or RasterBaseCoordinates.from_hgt_path(
            path
        )

        # We subtract one as each row overlaps the neighbouring raster by 1 pixel
        self.pixel_width = 1 / (self.values_per_row - 1)

    @classmethod
    def from_base_coordinates(cls, base_coordinates: RasterBaseCoordinates):
        return cls(
            path=get_hgt_path(base_coordinates.hgt_name),
            base_coordinates=base_coordinates,
        )

    def ensure_loaded(self, force=False):
        if not force and self.raster is not None:
            return

        if ".zip" in self.path.suffixes:
            zipped_files = ZipFile(self.path).namelist()
            zipped_files = [name for name in zipped_files if ".hgt" in name]
            assert len(zipped_files) == 1, (
                f"ZIP at {self.path} contains the wrong number of hgt files "
                f"({len(zipped_files)}!=1). Contains {zipped_files}"
            )
            self.raster = ZipFile(self.path).read(zipped_files[0])
        else:
            self.raster = self.path.read_bytes()

        self.validate()

    def validate(self):
        expected_bytes = self.expected_values * 2
        assert len(self.raster) == expected_bytes

    def get_height(self, x, y) -> int:
        """Get the height at the given pixel"""
        self.ensure_loaded()
        # Get the 1-indexed pixel number
        pixel_number = x + (y - 1) * self.values_per_row
        # Convert it ro be 0-indexed
        pixel_number -= 1

        byte_number = pixel_number * 2
        return int.from_bytes(
            self.raster[byte_number : byte_number + 2], byteorder="big"
        )

    def get_height_for_latitude_and_longitude(
        self, latitude: float, longitude: float
    ) -> int:
        """Get the height at the given lat/lng"""
        x, y = self._latitude_and_longitude_to_coordinates(latitude, longitude)
        return self.get_height(x, y)

    def _latitude_and_longitude_to_coordinates(
        self, latitude: float, longitude: float
    ) -> Tuple[int, int]:
        origin_latitude = self.base_coordinates.latitude + 1
        origin_longitude = self.base_coordinates.longitude
        latitude_offset = origin_latitude - latitude
        longitude_offset = longitude - origin_longitude

        if latitude_offset > 1 or latitude_offset < 0:
            raise ValueError(
                f"Latitude {latitude} with offset {latitude_offset} is not within "
                f"this heightmap of base coordinates {self.base_coordinates}"
            )
        if longitude_offset > 1 or longitude_offset < 0:
            raise ValueError(
                f"Longitude {longitude} with offset {longitude_offset} is not within "
                f"this heightmap of base coordinates {self.base_coordinates}"
            )

        # Add one because pixels are 1-indexed
        x = round(longitude_offset / self.pixel_width) + 1
        y = round(latitude_offset / self.pixel_width) + 1

        return x, y


class HeightMapCollection:
    height_maps: Dict[RasterBaseCoordinates, HeightMap]

    def __init__(self):
        self.height_maps = {}

    def build_file_index(self):
        self.height_maps = {}
        for hgt_path in HGT_DIR.glob("**/*.hgt*"):
            hgt_name = hgt_path.name.split(".")[0]
            self.height_maps[RasterBaseCoordinates.from_hgt_name(hgt_name)] = HeightMap(
                path=hgt_path
            )

    def get_height_map_for_latitude_and_longitude(
        self, latitude: float, longitude: float
    ) -> HeightMap:
        base = RasterBaseCoordinates.from_float(latitude, longitude)
        try:
            return self.height_maps[base]
        except KeyError:
            raise Exception(
                f"Height map for {base} not found. Have you called "
                f"build_file_index() on your heightmap collection?"
            )

    def get_height_for_latitude_and_longitude(
        self, latitude: float, longitude: float
    ) -> int:
        height_map = self.get_height_map_for_latitude_and_longitude(latitude, longitude)
        return height_map.get_height_for_latitude_and_longitude(latitude, longitude)

    def load_area(self, corner1: RasterBaseCoordinates, corner2: RasterBaseCoordinates):
        """Pre-load a specific area of height maps"""
        min_latitude = min(corner1.latitude, corner2.latitude)
        max_latitude = max(corner1.latitude, corner2.latitude)
        min_longitude = min(corner1.longitude, corner2.longitude)
        max_longitude = max(corner1.longitude, corner2.longitude)

        for height_map in self.height_maps.values():
            ok_latitude = (
                min_latitude <= height_map.base_coordinates.latitude <= max_latitude
            )
            ok_longitude = (
                min_longitude <= height_map.base_coordinates.longitude <= max_longitude
            )
            if ok_latitude and ok_longitude:
                height_map.ensure_loaded()

    def get_elevation_profile(
        self,
        start_latitude: float,
        start_longitude: float,
        end_latitude: float,
        end_longitude: float,
    ):
        # y = mx + c
        pass


def points_on_line(
    x1: float, y1: float, x2: float, y2: float
) -> Generator[Tuple[float, float], None, None]:
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

    x_range = range(x1, x2 + 1)
    if rev:
        x_range = reversed(x_range)

    for x in x_range:
        if issteep:
            yield y, x
        else:
            yield x, y
        error -= deltay
        if error < 0:
            y += ystep
            error += deltax
