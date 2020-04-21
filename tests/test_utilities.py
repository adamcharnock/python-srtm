from srtm.utilities import points_on_line, apply_curvature, StraightLineEquation, ElevationProfilePoint, get_clearances


def test_points_on_line():
    assert list(points_on_line(0, 0, 2, 2)) == [(0, 0), (1, 1), (2, 2)]
    assert list(points_on_line(2, 2, 0, 0)) == [(2, 2), (1, 1), (0, 0)]
    assert list(points_on_line(0, 0, 0, 0)) == [(0, 0)]


def test_apply_curvature_simple_odd():
    adjusted = apply_curvature(
        profile_points=[
            ElevationProfilePoint(10.1, -10, 0, 1000),
            ElevationProfilePoint(10.2, -10, 0, 2000),
            ElevationProfilePoint(10.3, -10, 0, 3000),
            ElevationProfilePoint(10.4, -10, 0, 4000),
            ElevationProfilePoint(10.5, -10, 0, 5000),
            ElevationProfilePoint(10.6, -10, 0, 6000),
            ElevationProfilePoint(10.7, -10, 0, 7000),
        ]
    )
    heights = [p.elevation for p in adjusted]
    assert heights[0] == heights[-1]
    assert heights[1] == heights[-2]
    assert heights[2] == heights[-3]
    assert heights[3] == 0


def test_apply_curvature_simple_even():
    adjusted = apply_curvature(
        profile_points=[
            ElevationProfilePoint(10.1, -10, 0, 1000),
            ElevationProfilePoint(10.2, -10, 0, 2000),
            ElevationProfilePoint(10.3, -10, 0, 3000),
            ElevationProfilePoint(10.5, -10, 0, 5000),
            ElevationProfilePoint(10.6, -10, 0, 6000),
            ElevationProfilePoint(10.7, -10, 0, 7000),
        ]
    )
    heights = [p.elevation for p in adjusted]
    assert heights[0] == heights[-1]
    assert heights[1] == heights[-2]
    assert heights[2] == heights[-3]


def test_straight_line_equation():
    line = StraightLineEquation.from_points(0, 0, 10, 10)
    assert line.c == 0
    assert line.y(x=5) == 5

    line = StraightLineEquation.from_points(10, 10, 0, 0)
    assert line.c == 0
    assert line.y(x=5) == 5

    line = StraightLineEquation.from_points(1, 10, 2, 11)
    assert line.c == 9
    assert line.y(x=3) == 12


def test_get_clearances():
    # lat, long, elevation, distance
    profile = [
        ElevationProfilePoint(None, None, 10, 0),
        ElevationProfilePoint(None, None, 5, 1),
        ElevationProfilePoint(None, None, 20, 2),
        ElevationProfilePoint(None, None, 10, 3),
    ]
    assert get_clearances(profile) == [0, 5, -10, 0]
    assert get_clearances(profile, 1, 1) == [1, 6, -9, 1]
