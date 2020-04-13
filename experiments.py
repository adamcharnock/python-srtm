from srtm import Srtm1HeightMapCollection
from srtm.utilities import get_clearances

will_lat =  40.103284
will_long =  -7.453766
adam_lat =  40.073772
adam_long =  -7.432998


srtm1_data = Srtm1HeightMapCollection()
profile = Srtm1HeightMapCollection().get_elevation_profile(will_lat, will_long, adam_lat, adam_long)
print(min(get_clearances(profile, start_elevation_offset=4, end_elevation_offset=6)))
