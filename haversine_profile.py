import cProfile

from srtm.utilities import haversine

def do_it():
    for _ in range(1, 1000000):
        haversine(1.23456, 2.23456, 3.23456, 4.23456)

cProfile.run('do_it()', filename='haversine.cprof')
