import os
from pathlib import Path

import pytest

from raytracer import RasterBaseCoordinates, HeightMap, get_hgt_path, HeightMapCollection


# RasterBaseCoordinates

def test_raster_base_coordinates_ne():
    assert RasterBaseCoordinates.from_float(
        latitude=40.1,
        longitude=5.1,
    ).hgt_name == 'N40E005'


def test_raster_base_coordinates_nw():
    assert RasterBaseCoordinates.from_float(
        latitude=40.1,
        longitude=-7.1,
    ).hgt_name == 'N40W008'


def test_raster_base_coordinates_se():
    assert RasterBaseCoordinates.from_float(
        latitude=-33.768549,
        longitude=18.504695,
    ).hgt_name == 'S34E018'


def test_raster_base_coordinates_sw():
    assert RasterBaseCoordinates.from_float(
        latitude=-7.956037,
        longitude=-14.357948,
    ).hgt_name == 'S08W015'


def test_raster_base_coordinates_zero():
    assert RasterBaseCoordinates.from_float(
        latitude=0.1,
        longitude=0.1,
    ).hgt_name == 'N00E000'


def test_raster_base_coordinates_from_hgt_name_ne():
    assert RasterBaseCoordinates.from_hgt_name('N40E005') == (40, 5)


def test_raster_base_coordinates_from_hgt_name_sw():
    assert RasterBaseCoordinates.from_hgt_name('S40W005') == (-40, -5)


# HeightMap


def test_get_value():
    height_map = HeightMap(path=get_hgt_path("N40W008"))
    # Values taken from raster parsed by postgis, loaded with raster2pgsql
    assert height_map.get_height(x=1, y=1) == 1130
    assert height_map.get_height(x=1, y=2) == 1137
    assert height_map.get_height(x=1201, y=1) == 317
    assert height_map.get_height(x=1, y=1201) == 620
    assert height_map.get_height(x=1201, y=1201) == 390


def test_latitude_and_longitude_to_coordinates_corner1():
    height_map = HeightMap(path=Path('/dummy/N40W008.hgt.zip'))
    # x,y = 1, 1
    assert height_map._latitude_and_longitude_to_coordinates(latitude=41, longitude=-8) == (1, 1)


def test_latitude_and_longitude_to_coordinates_corner2():
    height_map = HeightMap(path=Path('/dummy/N40W008.hgt.zip'))
    # x,y = 1201, 1201
    assert height_map._latitude_and_longitude_to_coordinates(latitude=40, longitude=-7) == (1201, 1201)


def test_latitude_and_longitude_to_coordinates_ne():
    height_map = HeightMap(path=Path('/dummy/N40E015.hgt.zip'))
    assert height_map._latitude_and_longitude_to_coordinates(latitude=40.6208333, longitude=15.101666) == (123, 456)


def test_latitude_and_longitude_to_coordinates_nw():
    height_map = HeightMap(path=Path('/dummy/N40W008.hgt.zip'))
    assert height_map._latitude_and_longitude_to_coordinates(latitude=40.6208333, longitude=-7.898333) == (123, 456)


def test_latitude_and_longitude_to_coordinates_se():
    height_map = HeightMap(path=Path('/dummy/S34E018.hgt.zip'))
    assert height_map._latitude_and_longitude_to_coordinates(latitude=-33.37916666, longitude=18.1016666) == (123, 456)


def test_latitude_and_longitude_to_coordinates_sw():
    height_map = HeightMap(path=Path('/dummy/S08W015.hgt.zip'))
    assert height_map._latitude_and_longitude_to_coordinates(latitude=-7.37916666666667, longitude=-14.8983333333333) == (123, 456)


def get_height_for_latitude_and_longitude():
    height_map = HeightMap.from_file(path=get_hgt_path("N40W008"))
    assert height_map.get_height_for_latitude_and_longitude(latitude=40, longitude=-7) == 390


# HeightMapCollection


def test_height_map_collection_build_file_index():
    collection = HeightMapCollection()
    collection.build_file_index()
    assert len(collection.height_maps) == 13967


def test_height_map_collection_get_height_for_latitude_and_longitude():
    collection = HeightMapCollection()
    collection.build_file_index()
    assert collection.get_height_for_latitude_and_longitude(latitude=40, longitude=-7) == 390

