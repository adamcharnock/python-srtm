import os
from pathlib import Path

import pytest

from raytracer import RasterBaseCoordinates, HeightMap, get_hgt_path


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

def test_height_map_from_file():
    assert HeightMap.from_file(
        path=get_hgt_path("N40W008")
    )
