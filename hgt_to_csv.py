from zipfile import ZipFile
import struct
from contextlib import contextmanager
from itertools import product, chain
from pathlib import Path
from typing import Optional, Dict
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tower_finder")

DATA_PATH = Path("/Volumes/General/srtm")
DATA_FILES: Dict[str, Path] = {
    p.name.split(".")[0]: p
    for p in chain(DATA_PATH.rglob("*.hgt.zip"), DATA_PATH.rglob("*.hgt"))
}


def get_file_name(lat, long):
    filename_lat = int(lat)
    filename_long = int(long)

    filename_ns = "S" if filename_lat < 0 else "N"
    filename_ew = "W" if filename_long < 0 else "E"

    return f"{filename_ns}{abs(filename_lat):0>2}{filename_ew}{abs(filename_long):0>3}"


@contextmanager
def open_srtm(lat, long):
    file_name = get_file_name(lat, long)
    path = DATA_FILES[file_name]

    logger.info(f"Opening {path}")

    if path.suffix == ".zip":
        with ZipFile(str(path)) as zip_file:
            assert zip_file.testzip() is None
            with zip_file.open(zip_file.filelist[0].filename, mode="r") as f:
                yield f
    else:
        with open(str(path), mode="rb") as f:
            yield f


def lat_long_to_file_position(lat: float, long: float) -> int:
    remainder_lat_arc_seconds = abs(lat - int(lat)) * 3600
    remainder_lng_arc_seconds = abs(long - int(long)) * 3600

    row = 1201 - round(remainder_lat_arc_seconds / 3) - 1
    col = round(remainder_lng_arc_seconds / 3) - 1

    position = row * 1201 + col
    return position


def position_to_lat_long(base_lat: int, base_long: int, position: int):
    row = 1201 - int(position / 1201) + 1
    col = position % 1201 + 1

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
    position = lat_long_to_file_position(lat, long)

    with open_srtm(lat, long) as f:
        print("-->", position)
        f.seek(position * 2)  # go to the right spot,
        buf = f.read(2)  # read two bytes and convert them:
        (val,) = struct.unpack(">h", buf)  # ">h" is a signed two byte integer
        if not val == -32768:  # the not-a-valid-sample value
            return val
        else:
            return None


def get_all():
    # lat_range = range(-90, 90)
    # long_range = range(-180, 180)
    lat_range = range(38, 40)
    long_range = range(-7, -5)

    for base_lat, base_long in product(lat_range, long_range):
        if get_file_name(base_lat, base_long) not in DATA_FILES:
            continue

        with open_srtm(base_lat, base_long) as f:
            data = f.read()

            if len(data) != 2884802:
                logger.warning(
                    f"Invalid length for file {f.name}, skipping. Expected 2,884,802, found {len(data)}. "
                    f"Consider unzipping this file manually and trying again."
                )
                continue

            for position in range(0, 1201 ** 2):
                index = position * 2
                (val,) = struct.unpack(">h", data[index : index + 2])
                if not val == -32768:
                    lat, lng = position_to_lat_long(base_lat, base_long, position)
                    yield val, lat, lng


if __name__ == "__main__":
    # print(get_sample(lat=0.39550467, long=29.70016479))  # Random, should be 1002m
    # print(get_sample(lat=0.5149772, long=29.87594604))  # Random, should be 2553m (mountainside)
    # print(get_sample(lat=0.92006544, long=29.93774414))  # Random, should be 844m

    # print(lat_long_to_file_position(lat=40.072509, long=-7.432258))
    # print(position_to_lat_long(base_lat=40, base_long=-7, position=1337232))

    SF = 10 ** 5
    for height, lat, long in get_all():
        print(
            ",".join(
                [str(height), str(round(lat * SF) / SF), str(round(long * SF) / SF)]
            )
        )


def test_position_to_lat_long():
    import pytest

    assert lat_long_to_file_position(10.007, 20.005) == 1431597
    assert pytest.approx(
        position_to_lat_long(base_lat=10, base_long=20, position=1434000), rel=0.0001
    ) == (10.007, 20.005)
    assert pytest.approx(
        position_to_lat_long(base_lat=-10, base_long=20, position=1434000), rel=0.0001
    ) == (-10.007, 20.005)
    assert pytest.approx(
        position_to_lat_long(base_lat=10, base_long=-20, position=1434000), rel=0.0001
    ) == (10.007, -20.005)
    assert pytest.approx(
        position_to_lat_long(base_lat=-10, base_long=-20, position=1434000), rel=0.0001
    ) == (-10.007, -20.005)
