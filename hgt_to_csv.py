import struct
from itertools import product
import os.path
from typing import Optional


def get_file_name(lat, long):
    filename_lat = int(lat)
    filename_long = int(long)

    filename_ns = 'S' if filename_lat < 0 else 'N'
    filename_ew = 'W' if filename_long < 0 else 'E'

    return f"{filename_ns}{abs(filename_lat):0>2}{filename_ew}{abs(filename_long):0>3}.hgt"


def lat_long_to_file_position(lat: float, long: float) -> int:
    remainder_lat_arc_seconds = abs(lat - int(lat)) * 3600
    remainder_lng_arc_seconds = abs(long - int(long)) * 3600

    row = 1201 - round(remainder_lat_arc_seconds / 3)
    col = round(remainder_lng_arc_seconds / 3) + 1

    position = row * 1201 + col
    return position


def position_to_lat_long(base_lat: int, base_long: int, position: int):
    row = 1201 - int(position / 1201)
    col = position % 1201

    remainder_lat_arc_seconds = row * 3
    remainder_lng_arc_seconds = col * 3

    if base_lat < 0:
        remainder_lat_arc_seconds = -remainder_lat_arc_seconds

    if base_long < 0:
        remainder_lng_arc_seconds = -remainder_lng_arc_seconds

    lat = base_lat + (remainder_lat_arc_seconds / 3600)
    long = base_long + (remainder_lng_arc_seconds / 3600)

    return lat, long


def get_sample(lat, long) -> Optional[int]:
    file_name = get_file_name(lat, long)
    position = lat_long_to_file_position(lat, long)

    with open(file_name, "rb") as f:

        print('-->', position)
        f.seek(position * 2)  # go to the right spot,
        buf = f.read(2)  # read two bytes and convert them:
        val, = struct.unpack('>h', buf)  # ">h" is a signed two byte integer
        if not val == -32768:  # the not-a-valid-sample value
            return val
        else:
            return None


def get_all():
    lat_range = range(-90, 90)
    long_range = range(-180, 180)

    for base_lat, base_long in product(lat_range, long_range):
        file_name = get_file_name(base_lat, base_long)

        if not os.path.exists(file_name):
            print('not found', file_name)
            continue

        with open(file_name, "rb") as f:
            data = f.read()

        for position in range(0, 1201 ^ 2):
            index = position*2
            val, = struct.unpack('>h', data[index:index+2])
            if not val == -32768:
                lat, lng = position_to_lat_long(base_lat, base_long, position)
                yield val, lat, lng


if __name__ == '__main__':
    # print(get_sample(lat=50.416358, long=14.919827))
    # print(get_sample(lat=0.38614545, long=29.86956589))  # Mount stanley
    print(get_sample(lat=0.39550467, long=29.70016479))  # Random, should be 1002m
    print(get_sample(lat=0.5149772, long=29.87594604))  # Random, should be 2553m
    print(get_sample(lat=0.92006544, long=29.93774414))  # Random, should be 844m

    # print(lat_long_to_file_position(lat=40.072509, long=-7.432258))
    # print(position_to_lat_long(base_lat=40, base_long=-7, position=1337232))

    # for x in get_all():
    #     print(x)

def test_position_to_lat_long():
    assert position_to_lat_long(base_lat=10, base_long=20, position=1434000) == (10.005, 20.005)
    assert position_to_lat_long(base_lat=-10, base_long=20, position=1434000) == (-10.005, 20.005)
    assert position_to_lat_long(base_lat=10, base_long=-20, position=1434000) == (10.005, -20.005)
    assert position_to_lat_long(base_lat=-10, base_long=-20, position=1434000) == (-10.005, -20.005)
