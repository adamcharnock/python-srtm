# Postgres with postgis 3

This process may prove useful if one needs to load the SRTM data
into Postgis. I used Postgis to create accurate values which 
I could test my implementation against.

```
docker run -v heightmap-data:/var/lib/postgresql/data -e POSTGRES_PASSWORD=postgres --name postgis -p 5433:5432 postgis/postgis:12-3.0

# password is postgres
psql -h127.0.0.1 -p5433 -dpostgres -Upostgres
create extension postgis_raster;
CREATE EXTENSION postgis_sfcgal;
```

# SQL from HGT files

```
cd /Volumes/General-1/srtm/version2_1/SRTM3
raster2pgsql -s 4236 -d -F -I -C -b 1 \
    Eurasia/N40W007.hgt.zip \
    Eurasia/N40W008.hgt.zip \
    Eurasia/N39W007.hgt.zip \
    Eurasia/N39W008.hgt.zip \
    Eurasia/N40E015.hgt.zip \
    Africa/S34E018.hgt.zip \
    Islands/S08W015.hgt.zip \
    public.heightmap \
    | psql -h127.0.0.1 -p5433 -dpostgres -Upostgres
```

# Load into postgres

```
# Passsord is "postgres" (set in docker run command above)
cat central_portugal.sql | psql -h127.0.0.1 -p5433 -dpostgres -Upostgres
```
