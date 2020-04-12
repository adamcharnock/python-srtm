from srtm.utilities import points_on_line, apply_curvature


def test_points_on_line():
    assert list(points_on_line(0, 0, 2, 2)) == [(0, 0), (1, 1), (2, 2)]
    assert list(points_on_line(2, 2, 0, 0)) == [(2, 2), (1, 1), (0, 0)]
    assert list(points_on_line(0, 0, 0, 0)) == [(0, 0)]


def test_apply_curvature_simple_odd():
    adjusted = apply_curvature(
        heights=[
            (10.1, -10, 0),
            (10.2, -10, 0),
            (10.3, -10, 0),
            (10.4, -10, 0),
            (10.5, -10, 0),
            (10.6, -10, 0),
            (10.7, -10, 0),
        ]
    )
    heights = [h for _, _, h in adjusted]
    assert heights[0] == heights[-1]
    assert heights[1] == heights[-2]
    assert heights[2] == heights[-3]
    assert heights[3] == 0


def test_apply_curvature_simple_even():
    adjusted = apply_curvature(
        heights=[
            (10.1, -10, 0),
            (10.2, -10, 0),
            (10.3, -10, 0),
            (10.5, -10, 0),
            (10.6, -10, 0),
            (10.7, -10, 0),
        ]
    )
    heights = [h for _, _, h in adjusted]
    assert heights[0] == heights[-1]
    assert heights[1] == heights[-2]
    assert heights[2] == heights[-3]
