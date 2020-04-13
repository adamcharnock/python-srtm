from time import time
import cProfile

from srtm import Srtm1HeightMapCollection, Srtm3HeightMapCollection
from srtm.utilities import get_clearances

will_lat =  40.103284
will_long =  -7.453766
adam_lat =  40.073772
adam_long =  -7.432998

bound1_lat = 40.064531
bound1_long = -7.400959
bound2_lat = 40.122604
bound2_long = -7.462507

print("Indexing files")
data = Srtm3HeightMapCollection()
data.build_file_index()

start = time()
print("Calculating profiles")


def permutations():
    points = list(data.get_points(bound1_lat, bound2_long, bound2_lat, bound1_long))

    iterations = 0
    for p1_lat, p1_long in points:
        p2_lat, p2_long = points[0]
        # for p2_lat, p2_long in points:
        get_clearances(
            data.get_elevation_profile(p1_lat, p1_long, p2_lat, p2_long)
        )
        iterations += 1

    print(f"Did {iterations} iterations in {time() - start} seconds")

cProfile.run('permutations()', filename='permutations.cprof')
