# %% --- header ---

# author:
# date created:
# email:

# script name: 04_get_nlcd_data.py

# script description: this script gets nlcd land cover data to run the
# plet module calculations

# to do:


# %% --- set up ---

# import libraries
import pandas
import geopandas
import numpy
import pygeohydro
import pyproj
from rioxarray import merge
import rioxarray
import rasterio
from xrspatial import zonal_crosstab
import os
import sys
import math
# import us
# import pynhd
# import pygeoutils
# import matplotlib.pyplot as plt

# set projection library
os.environ['PROJ_LIB'] = r"C:/Users/sheila.saia/AppData/Local/anaconda3/envs/esmc_env/Library/share/proj"
os.environ['PROJ_DATA'] = r"C:/Users/sheila.saia/AppData/Local/anaconda3/envs/esmc_env/Library/share/proj"

# check
# os.environ['PROJ_LIB']
# os.environ['PROJ_DATA']

# output paths
output_path = r"C:/Users/sheila.saia/OneDrive - Tetra Tech, Inc/Documents/github/2024-esmc-plet/data/"

# projection
wgs84_epsg = 4326
wgs84_epsg_proj = pyproj.CRS.from_user_input(wgs84_epsg)
wgs84_wkt = wgs84_epsg_proj.to_wkt()
# help: https://geopandas.org/en/stable/docs/user_guide/projections.html


# %% --- load data ----
# field data from esmc (this is test data for now)
field_data_raw = geopandas.read_file(output_path + "data/fields/esmc_test_fields.shp")
# field_data_raw
# field_data_raw.crs
field_data = field_data_raw.to_crs(epsg = wgs84_epsg).reset_index(drop = True)

# set fidle_id as index
field_data.index = field_data['field_id']

# make list of unique field ids
unique_field_list = field_data['field_id'].unique()

# check
# field_data
# type(field_data)
# field_data.columns
# field_data.crs
# crs is ok


# %% ---- get nlcd data for fields ----
# help: https://docs.hyriver.io/autoapi/pygeohydro/nlcd/index.html#module-pygeohydro.nlcd
# help: https://docs.hyriver.io/examples/notebooks/nlcd.html#

# create an nlcd data dictionary (from 2019, 30 m resolution)
# pull nlcd data in huc12 bounds
# field_nlcd_data_dictionary = pygeohydro.nlcd_bygeom(geometry = field_huc12_bounds, resolution = 30, years = {'cover': [2019]}, crs = wgs84_epsg, ssl = False)
# this has lots of rasterio warnings printing out but it seems to complete the request and return an output
# even have rasterio warnings after setting PROJ_LIB in path (not sure what's going on...)

# create an nlcd data dictionary (from 2019, 30 m resolution)
# pull for nlcd data in field bounds
field_nlcd_data_dictionary = pygeohydro.nlcd_bygeom(geometry = field_data, resolution = 30, years = {'cover': [2019]}, crs = wgs84_epsg, ssl = False)

# check data
# field_nlcd_data_dictionary.keys()
# field_nlcd_data_dictionary.items()
# type(field_nlcd_data_dictionary)
# unique_huc12_overlay_list.size # three huc12 basins, check

# need to streamline the code below so not separating out the first array from the others
# and also not growing an empty array row-wise
# need to add if statement checks in case there's no data

# loop through fields and merge into one dataset
for f in range(0, (unique_field_list.size)):
    # print(h)
    if f == 0:
        # get land cover array
        field_nlcd_merge = field_nlcd_data_dictionary[unique_field_list[f]].cover_2019

        # calculate stats
        temp_nlcd_stats = pygeohydro.cover_statistics(field_nlcd_merge)

        # conver to df
        field_nlcd_stats_pd_classes = pandas.DataFrame.from_dict(temp_nlcd_stats.classes, orient = 'index').reset_index()
        field_nlcd_stats_pd_categories = pandas.DataFrame.from_dict(temp_nlcd_stats.categories, orient = 'index').reset_index()

        # add column names
        field_nlcd_stats_pd_classes.columns = ['lc_desc', 'percent']
        field_nlcd_stats_pd_categories.columns = ['lc_desc', 'percent']

        # save df
        field_nlcd_stats_pd_classes['huc12'] = numpy.repeat(unique_field_list[f], field_nlcd_stats_pd_classes.shape[0], axis = 0)
        field_nlcd_stats_pd_categories['huc12'] = numpy.repeat(unique_field_list[f], field_nlcd_stats_pd_categories.shape[0], axis = 0)

    else:
        # get land cover array
        temp_nlcd = field_nlcd_data_dictionary[unique_field_list[f]].cover_2019

        # calculate stats
        temp_nlcd_stats = pygeohydro.cover_statistics(temp_nlcd)

        # conver to df
        temp_nlcd_stats_pd_classes = pandas.DataFrame.from_dict(temp_nlcd_stats.classes, orient = 'index').reset_index()
        temp_nlcd_stats_pd_categories = pandas.DataFrame.from_dict(temp_nlcd_stats.categories, orient = 'index').reset_index()

        # add column names
        temp_nlcd_stats_pd_classes.columns = ['lc_desc', 'percent']
        temp_nlcd_stats_pd_categories.columns = ['lc_desc', 'percent']

        # add huc12 id
        temp_nlcd_stats_pd_classes['huc12'] = numpy.repeat(unique_field_list[f], temp_nlcd_stats_pd_classes.shape[0], axis = 0)
        temp_nlcd_stats_pd_categories['huc12'] = numpy.repeat(unique_field_list[f], temp_nlcd_stats_pd_categories.shape[0], axis = 0)

        # append to df
        field_nlcd_stats_pd_classes = pandas.concat([field_nlcd_stats_pd_classes, temp_nlcd_stats_pd_classes]).reset_index(drop = True)
        field_nlcd_stats_pd_categories = pandas.concat([field_nlcd_stats_pd_categories, temp_nlcd_stats_pd_categories]).reset_index(drop = True)

        # merge field arrays
        field_nlcd_merge = merge.merge_arrays([field_nlcd_merge, temp_nlcd])
        print("merged " + str(f + 1) + " of " + str(unique_field_list.size) + " fields")

# export
# field_nlcd_merge.to_netcdf(output_path + "scratch/test_field_nlcd2019.nc")
# field_nlcd_stats_pd_classes.to_csv(output_path + "scratch/test_field_nlcd2019_class_stats.csv")
# field_nlcd_stats_pd_categories.to_csv(output_path + "scratch/test_field_nlcd2019_cat_stats.csv")

# classes are more detailed than categories (i.e., standard is 8 summary categories)

# check
# numpy.unique(field_nlcd_merge.data)
# field_nlcd_merge.size
# type(field_nlcd_merg)
# field_nlcd_stats_pd_classes.shape[0] 
# field_nlcd_stats_pd_categories.shape[0] # 5 fields x 8 categories = 40, check!


# %% ---- calculate nlcd zonal stats for each field ----
# nlcd metadata
# nlcd_classes_metadata = pandas.Series(pygeohydro.helpers.nlcd_helper()["classes"])

# function to create a transform for rasterio.rasterize
# def calculate_tranform (gdf_data, res = 30):
#     # set resolution
#     raster_res = res # meters

#     # get bounds, width, and height
#     min_x, min_y, max_x, max_y = data_bounds = gdf_data['geometry'].total_bounds
#     width_px = math.ceil((max_x - min_x) / raster_res)
#     height_px = math.ceil((max_y - min_y) / raster_res)

#     # calculate transform
#     transform = rasterio.transform.from_bounds(data_bounds[0], 
#                                                             data_bounds[1], 
#                                                             data_bounds[2], 
#                                                             data_bounds[3], 
#                                                             width_px, height_px)
# 
#     return transform

# calculate transform
# field_output_resolution = 30 / 111319.9
# field_raster_transform = calculate_tranform(gdf_data = field_data, res = field_output_resolution)

# nlcd xarray to rioxarray object
field_nlcd_merge_rio = field_nlcd_merge.rio
# type(field_nlcd_merge_rio)

# rasterize field bounds
field_geom = field_data[['geometry', 'id']].values.tolist() # this has to be id > must be unique
# field_rasterized = rasterio.features.rasterize(field_geom, out_shape = field_nlcd_merge.shape, transform = field_raster_transform) # this is not working
field_rasterized = rasterio.features.rasterize(field_geom, out_shape = field_nlcd_merge_rio.shape, all_touched = True, transform = field_nlcd_merge_rio.transform())
# help: https://pygis.io/docs/e_raster_rasterize.html

# check
# type(field_rasterized) # numpy array

# make copy of nlcd data and add rasterized field data to it
field_rasterized_xarray = field_nlcd_merge.copy()
field_rasterized_xarray.data = field_rasterized

# check
# field_rasterized_xarray.dims
# field_rasterized_xarray.sizes
# field_rasterized_xarray.size

# calculate number of cells in each nlcd class for each field (field = "zone")
field_zonal_crosstabs = zonal_crosstab(field_rasterized_xarray, field_nlcd_merge, nodata_values = 127)
# zone zero is the total of cells outside the field rasters

# calculate area for each nlcd from zonal_crosstabs output
field_zonal_crosstabs_area_sqm = field_zonal_crosstabs.iloc[:,1:].mul(30 * 30)
field_zonal_crosstabs_nlcd_cols = field_zonal_crosstabs_area_sqm.columns.tolist()
field_zonal_crosstabs_area_sqm['zone'] = field_zonal_crosstabs['zone']

# field info lookup
field_zone_lookup_part1 = field_data.drop(columns = 'geometry')
field_zone_lookup_part1['zone'] = field_data['id']
field_zone_lookup_part2 = pandas.DataFrame({'id': [0], 
                                            'field_id': ['non-field'], 
                                            'zone': [0]})
field_zone_lookup = pandas.concat([field_zone_lookup_part1, field_zone_lookup_part2], ignore_index = True).reset_index(drop = True)

# join field info with zonal crosstabs
field_zonal_crosstabs_area_join = field_zonal_crosstabs_area_sqm.join(field_zone_lookup.set_index('zone'), on = 'zone')
field_zonal_crosstabs_area_join['zonal_tot_area_sqkm'] = field_zonal_crosstabs_area_join[field_zonal_crosstabs_nlcd_cols].sum(axis = 1) / 1000**2
# still need to format this so it can be used as input into CN equations
# not sure why total areas calculated in zonal crosstabs are so far off and always lower than qgis areas (qgis area is 1.2 to 1.4 times higher)
# need to ask Brian about solutions for this
# maybe it's off because it's not projected (it's in wgs84)?
# i'm having trouble finding code to set the resolution of a dataset using rasterio.rasterize
# tried specifying resolution like here https://gis.stackexchange.com/questions/422146/specify-spatial-resolution-using-rasterio-rasterize but this didn't work (see comments above)


