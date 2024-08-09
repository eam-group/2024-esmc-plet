import geopandas as gpd
import os, random

def random_number():
    return random.randint(1, 12)

df = gpd.read_file(r'E:\Project Work\ESMC\02_Year 2\PLET_buildout\data\test_field_file.shp')
df = df.rename(columns={'Name':'SiteID'})

df['SiteID'] = df.index.to_series().apply(lambda x: f'ID_{x}')
df['year'] = 2019
df['n_months'] = df.apply(lambda row: random_number(), axis=1)
df['manure_area'] = df.apply(lambda row: random_number()*200.3, axis=1)
df['n_animals'] = df.apply(lambda row: random_number()*2, axis=1)
df['bmp_short_name'] = 'tempBMPname'
df['bmp_acres'] = df.apply(lambda row: random_number()*2256, axis=1)

df = gpd.GeoDataFrame(df)

out = r'E:\Project Work\ESMC\02_Year 2\PLET_buildout\data\test_field_file.geojson'

df.to_file(out)
