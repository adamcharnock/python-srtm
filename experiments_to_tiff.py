import gdal
import numpy
import pickle


with open("can_be_seen_counts.pickle", "rb") as f:
    data = pickle.load(f)

rows = 1201
cols = 1201
base_lat = 40.064531
base_long = -7.462507

with open("can_be_seen_counts.asc", "w") as f:
    f.write(f"ncols         {cols}\n")
    f.write(f"nrows         {rows}\n")
    f.write(f"xllcorner     {base_long}\n")
    f.write(f"yllcorner     {base_lat}\n")
    f.write(f"cellsize      {1/1200}\n")
    f.write(f"NODATA_value  {-1}")
    for n, v in enumerate(data.values()):
        if n % 1201 == 0:
            f.write("\n")
        else:
            f.write(" ")
        f.write(str(v))

