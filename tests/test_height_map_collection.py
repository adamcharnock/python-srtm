from srtm.base_coordinates import RasterBaseCoordinates
from srtm.height_map_collection import Srtm3HeightMapCollection, Srtm1HeightMapCollection


def test_srtm3_height_map_collection_build_file_index():
    collection = Srtm3HeightMapCollection()
    collection.build_file_index()
    assert len(collection.height_maps) == 13967


def test_srtm3_height_map_collection_get_height_for_latitude_and_longitude():
    collection = Srtm3HeightMapCollection()
    collection.build_file_index()
    assert (
        collection.get_altitude(latitude=40, longitude=-7)
        == 390
    )


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
        apply_earth_curvature=False
    )
    # lat, long, height
    assert profile[0] == (40.10324729392173, -7.453788509575354, 566)
    assert profile[-1] == (40.07410491257286, -7.432972522897585, 424)
    assert len(profile) == 36


def test_srtm1_height_map_collection_get_elevation_profile():
    collection = Srtm1HeightMapCollection()
    collection.build_file_index()
    profile = collection.get_elevation_profile(
        start_latitude=40.103284,
        start_longitude=-7.453766,
        end_latitude=40.073772,
        end_longitude=-7.432998,
        apply_earth_curvature=False
    )

    assert profile[0] == (40.103304637600665, -7.45376284365454, 563)
    assert profile[-1] == (40.07386836989725, -7.4329352957511805, 424)
    assert len(profile) == 107
