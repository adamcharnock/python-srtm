from srtm.utilities import points_on_line


def test_points_on_line():
    assert list(points_on_line(0, 0, 2, 2)) == [(0, 0), (1, 1), (2, 2)]
    assert list(points_on_line(2, 2, 0, 0)) == [(2, 2), (1, 1), (0, 0)]
    assert list(points_on_line(0, 0, 0, 0)) == [(0, 0)]
