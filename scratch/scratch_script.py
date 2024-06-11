#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@file-name:	scratch_script.py
@file-desc:   testing some things out for esmc mmrv automation
@date-created:   2024-02-21
@author:   sheila saia
@contact:	sheila.saia@tetratech.com
'''
# %% ---- notes and to do's ----

# notes-to-self
# when using mamba to install pynhd also need to install pyogrio and py7zr these will not be installed automatically as dependences of pynhd
# when using pygeoutils to get soil data also need to install planetary-computer
# for some reason i had to use pip to uninstall and then install lxml for pynhd to work
# needed to install rust and also install windows visual studio tools (see https://visualstudio.microsoft.com/visual-cpp-build-tools/ and https://doc.rust-lang.org/book/ch01-01-installation.html#installing-rustup-on-windows) before i could sucessfully install us library from pip
# nlcd classes metadata: https://data.usgs.gov/datacatalog/metadata/USGS.60cb3b86d34e86b938a305cb.xml
# this is summarized in nlcd_2019_legend.qml
# this is a helpful zonal stats tutorial: https://carpentries-incubator.github.io/geospatial-python/10-zonal-statistics.html


# to-do's
# 1. is there any easier way to convert bbox to a tuple? > look into this
# 2. not sure why areas are not checking for nlcd zonal crosstabs > ask Brian about this
# 3. zonal crosstabs stats results still need to be wrangled into proper format for plet calcs
# 4. get user input > will need to know whether a particular field is drained or not
# 5. * convert soil data to rasters and then calculate majority shg for each field > see notes on mukey issue


# %% ---- load libraries ----
import pandas
import geopandas
import numpy
import pynhd
import pygeohydro
import pyproj
from rioxarray import merge
import rioxarray
import rasterio
from xrspatial import zonal_crosstab
import os
import sys
import math
import us
import pygeoutils
import matplotlib.pyplot as plt

# get ssurgo functions
pysda_library_path = r"C:/Users/sheila.saia/OneDrive - Tetra Tech, Inc/Documents/github/2024-esmc-plet/functions/pysda"
sys.path.append(pysda_library_path)
import sdapoly, sdaprop #, sdainterp, sdawss
# help: https://github.com/ncss-tech/pysda


# %% ---- paths and projections ----
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
field_data_raw = geopandas.read_file(output_path + "scratch/esmc_test_fields.shp")
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

# %% ---- get huc12 bounds for state ----
# get state bounds for field_state
# help: https://pypi.org/project/us/

# field data location from esmc (this is test data for now)
field_state = "IL"

# write an expression to get the state specified
state_bounds_expression = "us.states.{state}.shapefile_urls()['state']".format(state = field_state)

# get state bounds data url (from census.gov)
state_bounds_url = eval(state_bounds_expression)

# read in state bounds zip file
state_bounds_raw = geopandas.read_file(state_bounds_url, engine = "pyogrio")
# this is giving a proj.db error but is still working

# check (and project if needed)
# state_bounds_raw.crs
# is a different crs than 4326 so need to project
state_bounds = state_bounds_raw.to_crs(epsg = wgs84_epsg)
# state_bounds
# state_bounds.crs
# checks now

# export
# state_bounds.to_file(filename = output_path + "scratch/test_state_bounds.shp")

# get bounding box for state bounds
state_bounds_bbox = state_bounds.bounds.to_numpy()
state_bounds_bbox_tuple = (state_bounds_bbox[0,0], state_bounds_bbox[0,1], state_bounds_bbox[0,2], state_bounds_bbox[0,3])

# get all huc12 bounds for a given bbox
state_huc12_bounds = pynhd.WaterData(layer = "wbd12").bybox(state_bounds_bbox_tuple).reset_index(drop = True)

# check
# state_huc12_bounds
# type(state_huc12_bounds)
# state_huc12_bounds.crs

# export
# state_huc12_bounds.to_file(filename = output_path + "scratch/test_state_huc12.shp")


# %% ---- get huc12 bounds for fields ----
field_huc12_overlay = geopandas.overlay(field_data, state_huc12_bounds, how = "intersection", keep_geom_type = False)

# check
# type(field_huc12_overlay)
# field_huc12_overlay.columns
# field_huc12_overlay.crs
# looks good

# this give subsets of the field data that overlap with the huc12 bounds
# could narrow this down to get unique huc12 id's and go from there to filter the whole dataset
# is there a more streamlined way to do this with

# make list of unique huc12 ids
unique_huc12_overlay_list = field_huc12_overlay['huc12'].unique()

# use list to make a boolean mask
unique_huc12_overlay_mask = state_huc12_bounds['huc12']. isin(unique_huc12_overlay_list)

# use mask to select out only huc12 bounds of interest
field_huc12_bounds = state_huc12_bounds[unique_huc12_overlay_mask]
# field_huc12_bounds.columns
# field_huc12_bounds['huc12']

# set huc12 as index
field_huc12_bounds.index = field_huc12_bounds['huc12']
# field_huc12_bounds.columns

# export
# field_huc12_bounds.to_file(filename = output_path + "scratch/test_field_huc12.shp")


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
field_nlcd_merge.to_netcdf(output_path + "scratch/test_field_nlcd2019.nc")
field_nlcd_stats_pd_classes.to_csv(output_path + "scratch/test_field_nlcd2019_class_stats.csv")
field_nlcd_stats_pd_categories.to_csv(output_path + "scratch/test_field_nlcd2019_cat_stats.csv")

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


# %% ---- get soils data for huc12 bounds ----
# try pysda functions
# intersect fields with ssurgo data info to get ssurgo aoi object
field_ssurgo_aoi = sdapoly.gdf(field_data)

# extra code/notes to self
# field_data_shp_path = r"C:/Users/sheila.saia/OneDrive - Tetra Tech, Inc/Documents/github/2024-esmc-plet/data/scratch/esmc_test_fields.shp"
# field_ssurgo_aoi = sdapoly.shp(field_data_shp_path)
# test_soils_db_path = r"C:/Users/sheila.saia/OneDrive - Tetra Tech, Inc/Documents/github/2024-esmc-plet/data/scratch"
# sdawss.availability(form = "shp", dest = test_soils_db_path)
# this takes 1-2 min to run and downloads zipped shp file (i.e., SoilDataAvailabilityShapefile.zip) to defined "dest" folder
# result is a map of counties in the entire us, not seeing any soil info
# sdawss.availability(form = "pdf", dest = test_soils_db_path)
# result is a pdf that shows where ssurgo data is complete/incomplete

# check
# type(field_ssurgo_aoi) # geopandas df
# field_ssurgo_aoi.columns # has ssurgo info in it

# get ssurgo soil hydro group data
field_shg = sdaprop.getprop(df = field_ssurgo_aoi, column = 'mukey', method = 'dom_comp_cat', prop = 'hydgrp', minmax = None, prnt = False, meta = False)
# if you set prnt = True you can see the sql call to the db
# use column id here for prop type: https://www.nrcs.usda.gov/sites/default/files/2022-08/SSURGO-Metadata-Tables-and-Columns-Report.pdf
# help on methods: https://github.com/ncss-tech/ssurgoOnDemand

# remove duplicate columns, join/merge the results, show first record
field_ssurgo_aoi_cols = field_ssurgo_aoi.columns.tolist()
field_shg_cols = field_shg.columns.tolist()
field_shg_cols_to_drop = [col for col in field_shg_cols if col in field_ssurgo_aoi_cols and col != 'mukey']
field_shg.drop(columns = field_shg_cols_to_drop, inplace = True)

# check
# field_shg

# join with mukey spatial data
field_shg_join = field_ssurgo_aoi.merge(field_shg, how = 'inner', on = 'mukey')

# function to reclassify shg for drainage/undrained
def reclass_shg_val(shg_val, type = 'undrained'):
    # if undrained then treat */D as shg class D
    if type == 'undrained':
        if shg_val in ['A', 'B', 'C', 'D']:
            return shg_val
        elif shg_val in ['A/D', 'B/D', 'C/D']:
            return 'D'
        else:
            print("shg value unknown")
            return None

    # if drained then treat */D as shg class *
    elif type == 'drained':
        if shg_val in ['A', 'B', 'C', 'D']:
            return shg_val
        elif shg_val in ['A/D', 'B/D', 'C/D']:
            return shg_val[0]
        else:
            print("shg value unknown")
            return None

    else:
        print("type must be either 'undrained' or 'drained'")
        return None
    
# test function
# reclass_shg_val('A', type = 'undrained')
# reclass_shg_val('A', type = 'drained')
# reclass_shg_val('A/D', type = 'undrained')
# reclass_shg_val('A/D', type = 'drained')
# works!

# add cases for drained and undrained (when shg has '/' in it)
# will need to know whether the field is drained or not
field_shg_join['shg_dr'] = [reclass_shg_val(h, type = "drained") for h in field_shg_join['hydgrp']]
field_shg_join['shg_undr'] = [reclass_shg_val(h, type = "undrained") for h in field_shg_join['hydgrp']]

field_shg_join_drain_simple = field_shg_join[['geometry', 'shg_dr']]
field_shg_join_undrain_simple = field_shg_join[['geometry', 'shg_undr']]

# check
# field_shg_join
# field_shg_join.columns
# type(field_shg_join)
# type(field_shg_join_drain_simple)
# field_shg_join_drain_simple.columns
# need to finish converting these to rasters and then running raster calcs for each field

# rasterize shg
# help: https://pygis.io/docs/e_raster_rasterize.html
field_shg_join_undrain_simple['id'] = list(range(0, len(field_shg_join_undrain_simple)))
field_geom_value_tuple = ((geom, value) for geom, value in zip(field_shg_join_undrain_simple.geometry, field_shg_join_undrain_simple['id']))
field_shg_undrain_rasterized = rasterio.features.rasterize(field_geom_value_tuple, 
                                                           out_shape = field_nlcd_merge_rio.shape,
                                                           transform = field_nlcd_merge_rio.transform(),
                                                           all_touched = True)

# this gives me each mukey but i need to match that mukey to the shg
# maybe rasterize the mukeys and then find a way to match that to the shg value

# export
field_shg_undrain_rasterized_path = output_path + "scratch/test_field_shg_undrain.tif"
with rasterio.open(
        field_shg_undrain_rasterized_path, "w",
        driver = "GTiff",
        crs = field_nlcd_merge_rio.crs,
        transform = field_nlcd_merge_rio.transform(),
        dtype = rasterio.uint8,
        count = 1,
        width = field_nlcd_merge_rio.width,
        height = field_nlcd_merge_rio.height) as dst:
    dst.write(field_shg_undrain_rasterized, indexes = 1)

# export
# field_shg_join.to_file(filename = output_path + "scratch/test_field_shg.shp")

# what other soils data do we need?


# test out pygeohydro library
# this is partially working but don't have access to all the ssurgo variables that are needed
# field_huc12_bounds
# test_field_geom = field_huc12_bounds.geometry[0]
# test_soil_data = pygeohydro.soil_properties()
# test_soil_data_mask = pygeoutils.xarray_geomask(test_soil_data, test_field_geom, field_huc12_bounds.crs)
# test_soil_data_sel = test_soil_data_mask.where(test_soil_data_mask.porosity > test_soil_data_mask.porosity.rio.nodata)
# test_soil_data_sel["porosity"] = test_soil_data_sel.porosity.rio.write_nodata(np.nan)
# _ = test_soil_data_sel.porosity.plot()
# test_soil_data_sel.porosity.attrs # to see info about this variable (unit, fill value, stats, etc.)
# export
# test_soil_data_sel.to_netcdf(output_path + "scratch/test_field_soils_onehuc12.nc")

# test out using soil_gnatsgo function
# this isn't working > submitted github issue for help
# test_basin = pynhd.NLDI().get_basins("11092450")
# test_basin_rasterio_wkt = rasterio.crs.CRS.from_wkt(test_basin.crs.to_wkt())
# test_basin_geom = test_basin.geometry["USGS-11092450"]
# test_soils_data = pygeohydro.soil_properties() # this runs with rasterio warnings but gives result
# test_soils_data_mask = pygeoutils.xarray_geomask(test_soil_data, test_basin_geom, test_basin_rasterio_wkt) # this runs fine, without errors
# i kept getting rasterio errors if i used test_basin.crs.to_wkt() here rather than test_basin_rasterio_wkt
# test_thickness_data = pygeohydro.soil_gnatsgo("tk0_999a", test_field_geom, test_basin_rasterio_wkt) # this has similar rasterio warnings as above but errors out with more rasterio errors
# test_mukey_data = pygeohydro.soil_gnatsgo("mukey", test_field_geom, field_huc12_bounds.crs)
 

# %% ---- scratch code ----

# calculate overland roughness
# field_huc12_roughness = pygeohydro.overland_roughness(test_sel_huc12_nlcd)

# plot of one huc12 bounds (land cover and roughness)
# from pyriver docs (https://docs.hyriver.io/examples/notebooks/nlcd.html#)
# fig, (ax1, ax2) = plt.subplots(1, 2, figsize = (9, 4))
# cmap, norm, levels = pygeohydro.plot.cover_legends()
# test_sel_huc12_nlcd.where(test_sel_huc12_nlcd < 127).plot(ax = ax1, cmap = cmap, levels = levels, cbar_kwargs={"ticks": levels[:-1]})
# ax1.set_title("Land Use/Land Cover 2019")
# ax1.set_axis_off()
# test_sel_huc12_roughness.plot(ax = ax2)
# ax2.set_title("Overland Roughness")
# ax2.set_axis_off()
# fig.savefig(output_path + "scratch/test_nlcd_figure_1v2.png", bbox_inches = "tight", facecolor = "w")

# plot of landcover for all selected huc12 bounds
# cmap, norm, levels = pygeohydro.plot.cover_legends()
# fig2, ax = plt.subplots(1, 1, figsize=(7, 7))
# xmin, ymin, xmax, ymax = field_huc12_bounds.unary_union.bounds
# test2_sel_huc12_nlcd = {h: data.cover_2019.where(data.cover_2019 < 127) for h, data in field_nlcd_data_dictionary.items()}
# type(test2_sel_huc12_nlcd)
# test2_sel_huc12_nlcd[unique_huc12_overlay_list[0]].plot(ax=ax, cmap=cmap, levels=levels, cbar_kwargs={"ticks": levels[:-1]})
# _= test2_sel_huc12_nlcd.pop(unique_huc12_overlay_list[0])
# for data in test2_sel_huc12_nlcd.values():
#     data.plot(ax = ax, cmap = cmap, levels = levels, add_colorbar = False)
# field_huc12_bounds.plot(ax = ax, facecolor = "none", edgecolor = "k", linewidth = 0.8)
# ax.set_xlim(xmin, xmax)
# ax.set_ylim(ymin, ymax)
# ax.set_title("Land Use/Land Cover 2019")
# ax.margins(0)
# ax.set_axis_off()
# fig2.savefig(output_path + "scratch/test_nlcd_figure_2v2.png", bbox_inches = "tight", facecolor = "w")

# export
# test2_sel_huc12_nlcd_merge.to_netcdf(output_path + "scratch/test_field_nlcd2019_2.nc")
# type(test2_sel_huc12_nlcd_merge)
# test2_sel_huc12_nlcd_merge
# i cannot figure out how to export this as a geotiff

# .merge(test2_sel_huc12_nlcd)

# get gage locations
# nldi = pynhd.NLDI()
# "05580950" (https://waterdata.usgs.gov/monitoring-location/05580950/#parameterCode=00065&period=P7D&showMedian=false)
# test = nldi.get_basins(feature_ids = "01031500")
# test2 = nldi.get_basins(feature_ids = "USGS-05580950")
# test2.crs # this says epsg is 4236 but the bounds are strange
# test2_wgs84 = test2.to_crs(epsg = wgs84_epsg)
# test2_wgs84.crs # this is the same
# was having issues with importing this into QGIS but i just needed to specify the crs in qgis and it showed up correctly (not in the indian ocean ha!)

# test3 = nldi.get_basins(feature_ids = "USGS-05580950")
# i'm not really sure what basin this is taking from (default is set to "nwissite" which is NWIS surface water sites but this bounds only sort of matches up with the associated huc12 id > "071300090701")

# export
# test2.to_file(filename = output_path + "scratch/esmc_test_gage.shp")

# loop through and merge into one dataset
# for h in range(0, (unique_huc12_overlay_list.size)):
#     # print(h)
#     if h == 0:
#         # get land cover array
#         field_nlcd_merge = field_nlcd_data_dictionary[unique_huc12_overlay_list[h]].cover_2019

#         # calculate stats
#         temp_nlcd_stats = pygeohydro.cover_statistics(field_nlcd_merge)

#         # conver to df
#         field_nlcd_stats_pd_classes = pandas.DataFrame.from_dict(temp_nlcd_stats.classes, orient = 'index').reset_index()
#         field_nlcd_stats_pd_categories = pandas.DataFrame.from_dict(temp_nlcd_stats.categories, orient = 'index').reset_index()

#         # add column names
#         field_nlcd_stats_pd_classes.columns = ['lc_desc', 'percent']
#         field_nlcd_stats_pd_categories.columns = ['lc_desc', 'percent']

#         # save df
#         field_nlcd_stats_pd_classes['huc12'] = numpy.repeat(unique_huc12_overlay_list[h], field_nlcd_stats_pd_classes.shape[0], axis = 0)
#         field_nlcd_stats_pd_categories['huc12'] = numpy.repeat(unique_huc12_overlay_list[h], field_nlcd_stats_pd_categories.shape[0], axis = 0)

#     else:
#         # get land cover array
#         temp_nlcd = field_nlcd_data_dictionary[unique_huc12_overlay_list[h]].cover_2019

#         # calculate stats
#         temp_nlcd_stats = pygeohydro.cover_statistics(temp_nlcd)

#         # conver to df
#         temp_nlcd_stats_pd_classes = pandas.DataFrame.from_dict(temp_nlcd_stats.classes, orient = 'index').reset_index()
#         temp_nlcd_stats_pd_categories = pandas.DataFrame.from_dict(temp_nlcd_stats.categories, orient = 'index').reset_index()

#         # add column names
#         temp_nlcd_stats_pd_classes.columns = ['lc_desc', 'percent']
#         temp_nlcd_stats_pd_categories.columns = ['lc_desc', 'percent']

#         # add huc12 id
#         temp_nlcd_stats_pd_classes['huc12'] = numpy.repeat(unique_huc12_overlay_list[h], temp_nlcd_stats_pd_classes.shape[0], axis = 0)
#         temp_nlcd_stats_pd_categories['huc12'] = numpy.repeat(unique_huc12_overlay_list[h], temp_nlcd_stats_pd_categories.shape[0], axis = 0)

#         # append to df
#         field_nlcd_stats_pd_classes = pandas.concat([field_nlcd_stats_pd_classes, temp_nlcd_stats_pd_classes]).reset_index(drop = True)
#         field_nlcd_stats_pd_categories = pandas.concat([field_nlcd_stats_pd_categories, temp_nlcd_stats_pd_categories]).reset_index(drop = True)

#         # merge field arrays
#         field_nlcd_merge = merge.merge_arrays([field_nlcd_merge, temp_nlcd])
#         print("merged " + str(h + 1) + " of " + str(unique_huc12_overlay_list.size) + "huc12 basin(s)")
