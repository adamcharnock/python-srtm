from pathlib import Path

from srtm.height_maps import HeightMap
from srtm.utilities import get_hgt_path


def test_get_value():
    height_map = HeightMap(path=get_hgt_path("N40W008"))
    # Values taken from raster parsed by postgis, loaded with raster2pgsql
    assert height_map.get_height(x=1, y=1) == 1130
    assert height_map.get_height(x=1, y=2) == 1137
    assert height_map.get_height(x=1201, y=1) == 317
    assert height_map.get_height(x=1, y=1201) == 620
    assert height_map.get_height(x=1201, y=1201) == 390


def test_latitude_and_longitude_to_coordinates_corner1():
    height_map = HeightMap(path=Path("/dummy/N40W008.hgt.zip"))
    # x,y = 1, 1
    assert height_map._latitude_and_longitude_to_coordinates(
        latitude=41, longitude=-8
    ) == (1, 1)


def test_latitude_and_longitude_to_coordinates_corner2():
    height_map = HeightMap(path=Path("/dummy/N40W008.hgt.zip"))
    # x,y = 1201, 1201
    assert height_map._latitude_and_longitude_to_coordinates(
        latitude=40, longitude=-7
    ) == (1201, 1201)


def test_latitude_and_longitude_to_coordinates_ne():
    height_map = HeightMap(path=Path("/dummy/N40E015.hgt.zip"))
    assert height_map._latitude_and_longitude_to_coordinates(
        latitude=40.6208333, longitude=15.101666
    ) == (123, 456)


def test_latitude_and_longitude_to_coordinates_nw():
    height_map = HeightMap(path=Path("/dummy/N40W008.hgt.zip"))
    assert height_map._latitude_and_longitude_to_coordinates(
        latitude=40.6208333, longitude=-7.898333
    ) == (123, 456)


def test_latitude_and_longitude_to_coordinates_se():
    height_map = HeightMap(path=Path("/dummy/S34E018.hgt.zip"))
    assert height_map._latitude_and_longitude_to_coordinates(
        latitude=-33.37916666, longitude=18.1016666
    ) == (123, 456)


def test_latitude_and_longitude_to_coordinates_sw():
    height_map = HeightMap(path=Path("/dummy/S08W015.hgt.zip"))
    assert height_map._latitude_and_longitude_to_coordinates(
        latitude=-7.37916666666667, longitude=-14.8983333333333
    ) == (123, 456)


def get_height_for_latitude_and_longitude():
    height_map = HeightMap.from_file(path=get_hgt_path("N40W008"))
    assert (
        height_map.get_height_for_latitude_and_longitude(latitude=40, longitude=-7)
        == 390
    )
