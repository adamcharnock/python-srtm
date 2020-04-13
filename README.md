# NASA SRTM altitude data parsing in Python

Provides an API onto SRTM `.hgt` or `.hgt.zip` files.

Requires Python 3.8, **may** work with Python 3.6 & 3.7.

## Installation

```
pip install python-srtm

export SRTM1_DIR=/path/to/srtm1/
export SRTM3_DIR=/path/to/srtm3/
```

## Use

You can access either SRTM1 or SRTM3 data. SRTM 1, for example:

```python
# SRTM1 - 30m resolution
>>> from srtm import Srtm1HeightMapCollection
>>> srtm1_data = Srtm1HeightMapCollection()
>>> srtm1_data.get_altitude(latitude=40.123, longitude=-7.456)
615
>>> Srtm1HeightMapCollection().get_elevation_profile(40.123, -7.456, 40.129, -7.460)
[615, 620, 618, 620, 616, 603, 593, 582, 575, 579, 580, 589, 589, 581, 565, 553, 545, 541, 534, 533, 529, 520, 514]
```

Or SRTM3:

```python
# SRTM3 - 90m resolution
>>> from srtm import Srtm3HeightMapCollection
>>> srtm3_data = Srtm3HeightMapCollection()
>>> srtm3_data.get_altitude(latitude=40.123, longitude=-7.456)
608
>>> Srtm3HeightMapCollection().get_elevation_profile(40.123, -7.456, 40.129, -7.460)
[626, 616, 585, 593, 577, 548, 528, 514]
```

## Profiling

```python
import cProfile
cProfile.run('function_to_profile()', filename='output.cprof')
```

```bash
brew install qcachegrind
pip install pyprof2calltree
pyprof2calltree -k -i /pythonprofiling/profiler/first_iteration.cprof
```

## Release process

For internal reference:

```
# Run the tests
pytest

# Update the setup.py
dephell convert
black setup.py

# Ensure poetry.lock is up to date
poetry lock

export VERSION="VERSION HERE"

# Version bump
poetry version $VERSION


# Commit
git add .
git commit -m "Releasing version $VERSION"

# Tagging and branching
git tag "v$VERSION"
git branch "v$VERSION"
git push origin \
    refs/tags/"v$VERSION" \
    refs/heads/"v$VERSION" \
    master

poetry publish --build
```
