from srtm.base_coordinates import RasterBaseCoordinates


def test_raster_base_coordinates_ne():
    assert (
        RasterBaseCoordinates.from_float(latitude=40.1, longitude=5.1,).file_name
        == "N40E005"
    )


def test_raster_base_coordinates_nw():
    assert (
        RasterBaseCoordinates.from_float(latitude=40.1, longitude=-7.1,).file_name
        == "N40W008"
    )


def test_raster_base_coordinates_se():
    assert (
        RasterBaseCoordinates.from_float(
            latitude=-33.768549, longitude=18.504695,
        ).file_name
        == "S34E018"
    )


def test_raster_base_coordinates_sw():
    assert (
        RasterBaseCoordinates.from_float(
            latitude=-7.956037, longitude=-14.357948,
        ).file_name
        == "S08W015"
    )


def test_raster_base_coordinates_zero():
    assert (
        RasterBaseCoordinates.from_float(latitude=0.1, longitude=0.1,).file_name
        == "N00E000"
    )


def test_raster_base_coordinates_from_file_name_ne():
    assert RasterBaseCoordinates.from_file_name("N40E005") == (40, 5)


def test_raster_base_coordinates_from_file_name_sw():
    assert RasterBaseCoordinates.from_file_name("S40W005") == (-40, -5)
