from pathlib import Path
from typing import Dict, Type

from srtm.base_coordinates import RasterBaseCoordinates
from srtm.utilities import points_on_line, SRTM3_DIR, SRTM1_DIR, apply_curvature
from srtm.height_maps import HeightMap, Srtm3HeightMap, Srtm1HeightMap


class HeightMapCollection:
    """ Provides access to data across all SRTM files

    This will lazy load data as needed
    """
    height_maps: Dict[RasterBaseCoordinates, HeightMap]
    height_map_class: Type[HeightMap] = None
    hgt_dir: Path = None

    def __init__(self, auto_build_index=True):
        self.height_maps = {}
        if auto_build_index:
            self.build_file_index()

        assert self.height_map_class, (
            "Error, use Srtm3HeightMapCollection or Srtm1HeightMapCollection"
        )

    def build_file_index(self):
        """Load an index of all available files

        This reads file names, but does not load the contained data.
        This is lazy-loaded on demand
        """
        self.height_maps = {}
        for hgt_path in self.hgt_dir.glob("**/*.hgt*"):
            hgt_name = hgt_path.name.split(".")[0]
            self.height_maps[RasterBaseCoordinates.from_file_name(hgt_name)] = self.height_map_class(
                path=hgt_path
            )

    def get_height_map_for_latitude_and_longitude(
        self, latitude: float, longitude: float
    ) -> HeightMap:
        """Get the HeightMap for the given latitude and longitude"""
        base = RasterBaseCoordinates.from_float(latitude, longitude)
        try:
            return self.height_maps[base]
        except KeyError:
            raise Exception(
                f"Height map for {base} not found. Have you called "
                f"build_file_index() on your heightmap collection?"
            )

    def get_altitude(
        self, latitude: float, longitude: float
    ) -> int:
        """Get the height of the given latitude and longitude"""
        height_map = self.get_height_map_for_latitude_and_longitude(latitude, longitude)
        return height_map.get_altitude_for_latitude_and_longitude(latitude, longitude)

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
        apply_earth_curvature=True,
    ):
        """Get the elevation profile between the two points given"""
        values_per_degree = self.height_map_class.values_per_row

        def to_int(lat_lng: float) -> int:
            return round(lat_lng * values_per_degree)

        def to_float(lat_lng_int: int) -> float:
            return lat_lng_int / values_per_degree

        points = points_on_line(
            x1=to_int(start_latitude),
            y1=to_int(start_longitude),
            x2=to_int(end_latitude),
            y2=to_int(end_longitude),
        )
        converted_points = [(to_float(x), to_float(y)) for x, y in points]

        elevations = []
        for latitude, longitude in converted_points:
            elevations.append((latitude, longitude, self.get_altitude(
                latitude, longitude
            )))

        if apply_earth_curvature:
            elevations = apply_curvature(elevations)

        return elevations


class Srtm3HeightMapCollection(HeightMapCollection):
    height_map_class = Srtm3HeightMap
    hgt_dir = SRTM3_DIR


class Srtm1HeightMapCollection(HeightMapCollection):
    height_map_class = Srtm1HeightMap
    hgt_dir = SRTM1_DIR
