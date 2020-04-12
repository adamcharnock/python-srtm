# Attempt 2
import math
from typing import NamedTuple, Dict


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
    rasters: Dict[RasterBaseCoordinates, bytes]

    def load(self):
        pass

