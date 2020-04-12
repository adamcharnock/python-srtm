# Attempt 2
import math
import os
from pathlib import Path
from typing import NamedTuple, Dict
from zipfile import ZipFile

HGT_DIR = Path(os.environ['SRTM_DIR'])
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
    assert False, f"Path for HGT name {hgt_name} could not be found. Perhaps there is no file for those coordinates?"


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
        assert hgt_name[0] in ('N', 'S'), error
        assert hgt_name[3] in ('E', 'W'), error
        try:
            is_north = hgt_name[0] == 'N'
            latitude = int(hgt_name[1:3])
            is_east = hgt_name[3] == 'E'
            longitude = int(hgt_name[4:7])
        except ValueError:
            assert False, error

        if not is_north:
            latitude *= -1
        if not is_east:
            longitude *= -1

        return cls(
            latitude=latitude,
            longitude=longitude
        )

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
    raster: bytes
    base_coordinates: RasterBaseCoordinates
    expected_values = 1442401
    values_per_row = 1201

    def __init__(self, raster, base_coordinates):
        self.raster = raster
        self.base_coordinates = base_coordinates

    @classmethod
    def from_file(cls, path: Path):
        hgt_name = path.name.split('.')[0]

        if '.zip' in path.suffixes:
            zipped_files = ZipFile(path).namelist()
            zipped_files = [name for name in zipped_files if '.hgt' in name]
            assert len(zipped_files) == 1, (
                f"ZIP at {path} contains the wrong number of hgt files "
                f"({len(zipped_files)}!=1). Contains {zipped_files}"
            )
            contents = ZipFile(path).read(zipped_files[0])
        else:
            contents = path.read_bytes()

        height_map = cls(
            raster=contents,
            base_coordinates=RasterBaseCoordinates.from_hgt_name(hgt_name)
        )
        height_map.validate()
        return height_map

    @classmethod
    def from_base_coordinates(cls, base_coordinates: RasterBaseCoordinates):
        return cls.from_file(
            path=get_hgt_path(base_coordinates.hgt_name)
        )

    def validate(self):
        expected_bytes = self.expected_values * 2
        assert len(self.raster) == expected_bytes

    def get_height(self, x, y):
        # Get the 1-indexed pixel number
        pixel_number = x + (y - 1) * self.values_per_row
        # Convert it ro be 0-indexed
        pixel_number -= 1

        byte_number = pixel_number * 2
        return int.from_bytes(self.raster[byte_number:byte_number+2], byteorder="big")

    def get_height_for_latitude_and_longitude(self, latitude: float, longitude: float):
        pass


class HeightMapCollection:
    rasters: Dict[RasterBaseCoordinates, bytes]

    def load(self):
        pass

