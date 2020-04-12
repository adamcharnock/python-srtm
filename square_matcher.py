from typing import NamedTuple, Tuple, Optional

SQUARE_SIZE = 3 / 3600


class Point(NamedTuple):
    lat: float
    long: float


class Square(NamedTuple):
    # Size in degrees
    center: Point
    size: float

    @property
    def min_corner(self):
        return Point(
            lat=self.center.lat - self.size / 2,
            long=self.center.long - self.size / 2,
        )

    @property
    def max_corner(self):
        return Point(
            lat=self.center.lat + self.size / 2,
            long=self.center.long + self.size / 2,
        )

    def contains(self, point: Point):
        return (
            self.min_corner.lat < point.lat <= self.max_corner.lat
            and self.min_corner.long < point.long <= self.max_corner.long
        )

    def __contains__(self, point: Point):
        return self.contains(point)

    @classmethod
    def nearest_to(cls, point: Point, square_size: float):
        # TODO: Always rounds down
        return Square(
            center=Point(
                lat=round(point.lat * square_size) / square_size,
                long=round(point.long * square_size) / square_size,
            ),
            size=square_size,
        )


class Line(NamedTuple):
    start: Point
    end: Point

    @property
    def equation(self) -> Tuple[Optional[float], Optional[float]]:
        try:
            gradient = (self.end.lat - self.start.lat) / (self.end.long - self.start.long)
        except ZeroDivisionError:
            return None, None

        intercept = self.end.lat - gradient * self.end.long
        return gradient, intercept

    def get_lat(self, long):
        gradient, intercept = self.equation
        if gradient is None:
            return self.end.lat
        return gradient * long + intercept

    def get_next_point(self, point: Point, distance: float):
        lat_delta = distance / gradient  # NO, pythag
        long_delta = distance * gradient


def get_squares(start: Point, end: Point, square_size: float = SQUARE_SIZE):
    line = Line(start, end)

    starting_square = Square.nearest_to(start, square_size)
    next_point = starting_square.center
    assert start in starting_square
    squares = [starting_square]

    while next_point < end:
        next_point = Point(
            long=next_point.long + square_size,
            lat=line.get_lat(long=next_point.lat + square_size)
        )
        squares.append(Square.nearest_to(next_point, square_size))

    return squares

if __name__ == '__main__':
    pass


def test_square_contains():
    assert Square(Point(10, 10), 1).contains(Point(10.1, 10.1))
    assert Square(Point(10, 10), 1).contains(Point(10.5, 10.5))
    assert Square(Point(-10, -10), 1).contains(Point(-10.1, -10.1))

    assert not Square(Point(10, 10), 1).contains(Point(10.6, 10.6))
    assert not Square(Point(10, 10), 1).contains(Point(9.5, 9.5))
    assert not Square(Point(-10, -10), 1).contains(Point(-10.6, -10.6))


def test_line():
    assert Line(Point(0, 0), Point(1, 1)).equation == (1, 0)
    assert Line(Point(1, 1), Point(0, 0)).equation == (1, 0)
    assert Line(Point(0, 1), Point(1, 0)).equation == (-1, 1)


def test_get_squares_diagonal():
    assert get_squares(
        start=Point(0, 0),
        end=Point(1, 1),
        square_size=1,
    ) == [
        Square(center=Point(lat=0.0, long=0.0), size=1),
        Square(center=Point(lat=1.0, long=1.0), size=1),
    ]


def test_get_squares_vertical():
    assert get_squares(
        start=Point(0, 0),
        end=Point(0, 1),
        square_size=1,
    ) == [
        Square(center=Point(lat=0.0, long=0.0), size=1),
        Square(center=Point(lat=0.0, long=1.0), size=1),
    ]


def test_get_squares_horizontal():
    # TODO: This is where it breaks down because we assume the line isn't flat
    assert get_squares(
        start=Point(0, 0),
        end=Point(1, 0),
        square_size=1,
    ) == [
        Square(center=Point(lat=0.0, long=0.0), size=1),
        Square(center=Point(lat=1.0, long=0.0), size=1),
    ]
