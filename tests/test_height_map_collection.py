from srtm.base_coordinates import RasterBaseCoordinates
from srtm.height_map_collection import (
    Srtm3HeightMapCollection,
    Srtm1HeightMapCollection,
)


def test_srtm3_height_map_collection_build_file_index():
    collection = Srtm3HeightMapCollection()
    assert len(collection.height_maps) == 13967


def test_srtm3_height_map_collection_get_height_for_latitude_and_longitude():
    collection = Srtm3HeightMapCollection()
    assert collection.get_altitude(latitude=40, longitude=-7) == 390


def test_srtm3_height_map_collection_load_area():
    collection = Srtm3HeightMapCollection()
    collection.build_file_index()
    collection.load_area(
        RasterBaseCoordinates.from_file_name("N38W006"),
        RasterBaseCoordinates.from_file_name("N40W008"),
    )
    loaded_height_maps = [hm for hm in collection.height_maps.values() if hm.raster]
    assert len(loaded_height_maps) == 9


def test_srtm3_height_map_collection_get_elevation_profile():
    collection = Srtm3HeightMapCollection()
    collection.build_file_index()
    profile = collection.get_elevation_profile(
        start_latitude=40.103284,
        start_longitude=-7.453766,
        end_latitude=40.073772,
        end_longitude=-7.432998,
        apply_earth_curvature=False,
    )
    # lat, long, height
    assert profile[0].latitude == 40.10324729392173
    assert profile[0].longitude == -7.453788509575354
    assert profile[0].elevation == 566
    assert profile[0].distance == 4.509638213110301

    assert profile[-1].latitude == 40.07410491257286
    assert profile[-1].longitude == -7.432972522897585
    assert profile[-1].elevation == 424
    assert profile[-1].distance == 3696.587861535811

    assert len(profile) == 36


def test_srtm1_height_map_collection_get_elevation_profile():
    collection = Srtm1HeightMapCollection()
    collection.build_file_index()
    profile = collection.get_elevation_profile(
        start_latitude=40.103284,
        start_longitude=-7.453766,
        end_latitude=40.073772,
        end_longitude=-7.432998,
        apply_earth_curvature=False,
    )

    assert profile[0].latitude == 40.103304637600665
    assert profile[0].longitude == -7.45376284365454
    assert profile[0].elevation == 564
    assert profile[0].distance == 2.3111704885835263

    assert profile[-1].latitude == 40.07386836989725
    assert profile[-1].longitude == -7.4329352957511805
    assert profile[-1].elevation == 425
    assert profile[-1].distance == 3721.2192128118545

    assert len(profile) == 107


def test_srtm3_get_points():
    collection = Srtm3HeightMapCollection(auto_build_index=False)
    points = list(collection.get_points(10, 50, 10.0083, 50.0083))

    assert points[0] == (10.0, 50.0)
    assert points[9] == (10.007499999999993, 50.0)
    assert points[10] == (10.0, 50.00083333333333)
    assert points[-1] == (10.007499999999993, 50.00749999999999)
    assert len(points) == 100
