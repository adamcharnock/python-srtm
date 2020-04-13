from pathlib import Path
from typing import NamedTuple


class RasterBaseCoordinates(NamedTuple):
    """Base coordinates for a SRTM HGT raster file

    HGT files are named based on the coordinate of their lower-left corner
    """

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
    def from_file_name(cls, hgt_name: str):
        """Create an instance from a HGT name, eg "N38W006" """
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
    def from_file_path(cls, path: Path):
        """Create an instance from a path to a HGT file"""
        return cls.from_file_name(hgt_name=path.name.split(".")[0])

    @property
    def file_name(self):
        """Get the expected HGT file name for these base coordinates (without file extension)"""
        if self.latitude >= 0:
            latitude = f"N{self.latitude:0>2}"
        else:
            latitude = f"S{-self.latitude:0>2}"

        if self.longitude >= 0:
            longitude = f"E{self.longitude:0>3}"
        else:
            longitude = f"W{-self.longitude:0>3}"

        return f"{latitude}{longitude}"
