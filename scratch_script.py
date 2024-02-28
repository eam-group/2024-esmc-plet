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
# 2. not sure why areas are not checking for nlcd zonal stats > look into this
# 3. zonal stats results need to be wrangled into proper format for plet
# 4. 

# %% ---- load libraries ----
import pandas
import geopandas
import numpy
import pynhd
import pygeohydro
import pygeoutils
import pyproj
import matplotlib.pyplot as plt
from rioxarray import merge
import rioxarray
import rasterio
from xrspatial import zonal_crosstab
import us
import os
import sys


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

# get ssurgo functions
pysda_library_path = r"C:/Users/sheila.saia/OneDrive - Tetra Tech, Inc/Documents/github/2024-esmc-plet/functions/pysda"
sys.path.append(pysda_library_path)
import sdapoly, sdaprop, sdainterp, sdawss


# %% --- load data ----
# field data from esmc (this is test data for now)
field_data_raw = geopandas.read_file(output_path + "scratch/esmc_test_fields.shp")
# field_data_raw
# field_data_raw.crs
field_data = field_data_raw.to_crs(epsg = wgs84_epsg).reset_index(drop = True)

# calculate areas
field_data['area_sqm'] = field_data['geometry'].area

# check data
# field_data
# field_data.crs
# type(field_data)
# crs is no properly set, check!

# %% ---- use state bounds to get huc12 bounds ----
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


# %% ---- get huc12 bounds that overlap with fields ----
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
field_huc12_bounds

# export
#field_huc12_bounds.to_file(filename = output_path + "scratch/test_field_huc12.shp")


# %% ---- get nlcd data for huc12 bounds ----
# help: https://docs.hyriver.io/autoapi/pygeohydro/nlcd/index.html#module-pygeohydro.nlcd
# help: https://docs.hyriver.io/examples/notebooks/nlcd.html#

# create an nlcd data dictionary (from 2019, 30 m resolution)
field_nlcd_data_dictionary = pygeohydro.nlcd_bygeom(geometry = field_huc12_bounds, resolution = 30, years = {'cover': [2019]}, crs = wgs84_epsg, ssl = False)
# this has lots of rasterio warnings printing out but it seems to complete the request and return an output
# even have rasterio warnings after setting PROJ_LIB in path (not sure what's going on...)

# check data
# field_nlcd_data_dictionary.keys
# field_nlcd_data_dictionary.items()
# type(field_nlcd_data_dictionary)
# unique_huc12_overlay_list.size # three huc12 basins, check

# need to streamline the code below so not separating out the first array from the others
# and also not growing an empty array row-wise
# need to add if statement checks in case there's no data

# loop through and merge into one dataset
for h in range(0, (unique_huc12_overlay_list.size)):
    # print(h)
    if h == 0:
        # get land cover array
        field_nlcd_merge = field_nlcd_data_dictionary[unique_huc12_overlay_list[h]].cover_2019

        # calculate stats
        temp_nlcd_stats = pygeohydro.cover_statistics(field_nlcd_merge)

        # conver to df
        field_nlcd_stats_pd_classes = pandas.DataFrame.from_dict(temp_nlcd_stats.classes, orient = 'index').reset_index()
        field_nlcd_stats_pd_categories = pandas.DataFrame.from_dict(temp_nlcd_stats.categories, orient = 'index').reset_index()

        # add column names
        field_nlcd_stats_pd_classes.columns = ['lc_desc', 'percent']
        field_nlcd_stats_pd_categories.columns = ['lc_desc', 'percent']

        # save df
        field_nlcd_stats_pd_classes['huc12'] = numpy.repeat(unique_huc12_overlay_list[h], field_nlcd_stats_pd_classes.shape[0], axis = 0)
        field_nlcd_stats_pd_categories['huc12'] = numpy.repeat(unique_huc12_overlay_list[h], field_nlcd_stats_pd_categories.shape[0], axis = 0)

    else:
        # get land cover array
        temp_nlcd = field_nlcd_data_dictionary[unique_huc12_overlay_list[h]].cover_2019

        # calculate stats
        temp_nlcd_stats = pygeohydro.cover_statistics(temp_nlcd)

        # conver to df
        temp_nlcd_stats_pd_classes = pandas.DataFrame.from_dict(temp_nlcd_stats.classes, orient = 'index').reset_index()
        temp_nlcd_stats_pd_categories = pandas.DataFrame.from_dict(temp_nlcd_stats.categories, orient = 'index').reset_index()

        # add column names
        temp_nlcd_stats_pd_classes.columns = ['lc_desc', 'percent']
        temp_nlcd_stats_pd_categories.columns = ['lc_desc', 'percent']

        # add huc12 id
        temp_nlcd_stats_pd_classes['huc12'] = numpy.repeat(unique_huc12_overlay_list[h], temp_nlcd_stats_pd_classes.shape[0], axis = 0)
        temp_nlcd_stats_pd_categories['huc12'] = numpy.repeat(unique_huc12_overlay_list[h], temp_nlcd_stats_pd_categories.shape[0], axis = 0)

        # append to df
        field_nlcd_stats_pd_classes = pandas.concat([field_nlcd_stats_pd_classes, temp_nlcd_stats_pd_classes]).reset_index(drop = True)
        field_nlcd_stats_pd_categories = pandas.concat([field_nlcd_stats_pd_categories, temp_nlcd_stats_pd_categories]).reset_index(drop = True)

        # merge field arrays
        field_nlcd_merge = merge.merge_arrays([field_nlcd_merge, temp_nlcd])
        print("merged " + str(h + 1) + " of " + str(unique_huc12_overlay_list.size) + "huc12 basin(s)")

# export
field_nlcd_merge.to_netcdf(output_path + "scratch/test_field_nlcd2019_allhuc12.nc")
field_nlcd_stats_pd_classes.to_csv(output_path + "scratch/test_field_nlcd2019_allhuc12_class_stats.csv")
field_nlcd_stats_pd_categories.to_csv(output_path + "scratch/test_field_nlcd2019_allhuc12_cat_stats.csv")

# classes are more detailed than categories (i.e., standard is 8 summary categories)

# check
# numpy.unique(field_nlcd_merge.data)
# field_nlcd_merge.size
# type(field_nlcd_merg)
# field_nlcd_stats_pd_classes.shape[0] 
# field_nlcd_stats_pd_categories.shape[0] # 3 hucs x 8 categories = 24, check!


# %% ---- calculate nlcd zonal stats for each field ----
# nlcd metadata
# nlcd_classes_metadata = pandas.Series(pygeohydro.helpers.nlcd_helper()["classes"])

# nlcd xarray to rioxarray object
field_nlcd_merge_rio = field_nlcd_merge.rio
# type(field_nlcd_merge_rio)

# rasterize field bounds
field_geom = field_data[['geometry', 'id']].values.tolist() # this has to be "id" > cannot work with "field_id" and i'm not sure why
field_rasterized = rasterio.features.rasterize(field_geom, out_shape = field_nlcd_merge.shape, transform = field_nlcd_merge_rio.transform())
# type(field_rasterized)

# make copy of nlcd data and add rasterized field data to it
field_rasterized_xarray = field_nlcd_merge.copy()
field_rasterized_xarray.data = field_rasterized

# calculate number of cells in each nlcd class for each field (field = "zone")
field_zonal_crosstabs = zonal_crosstab(field_rasterized_xarray, field_nlcd_merge, nodata_values = 127)
# zone zero is the total of cells outside the field rasters

# field info lookup
field_zone_lookup_part1 = field_data.drop(columns = 'geometry')
field_zone_lookup_part1['zone'] = field_data['id']
field_zone_lookup_part2 = pandas.DataFrame({'id': [0], 
                                            'field_id': ['non-field'], 
                                            'zone': [0]})
field_zone_lookup = pandas.concat([field_zone_lookup_part1, field_zone_lookup_part2], ignore_index = True).reset_index(drop = True)

# join field info with zonal crosstabs
field_zonal_crosstabs_join = field_zonal_crosstabs.join(field_zone_lookup.set_index('zone'), on = 'zone')
# still need to format this so it can be used as input into CN equations
# would need to multiple the counts for each nlcd type by area of the cell (3 x 30 m) to get total area
(sum(field_zonal_crosstabs_join.iloc[1,1:-2]) * (30 * 30) ) / 1000**2
# for field #1 i'm getting 1.4 sqkm here, but i'm getting 1.9 sqkm in QGIS...
# for field #4 i'm getting 0.99 sqkm here, but i'm getting 1.3 sqkm in QGIS...
# maybe it's off because it's not projected (it's in wgs84)?

# get the crs
# field_nlcd_merge_rio.crs


# %% ---- get soils data for huc12 bounds ----

field_huc12_bounds
test_field_geom = field_huc12_bounds.geometry[0]
test_soil_data = pygeohydro.soil_properties()
test_soil_data_mask = pygeoutils.xarray_geomask(test_soil_data, test_field_geom, field_huc12_bounds.crs)
test_soil_data_sel = test_soil_data_mask.where(test_soil_data_mask.porosity > test_soil_data_mask.porosity.rio.nodata)
test_soil_data_sel["porosity"] = test_soil_data_sel.porosity.rio.write_nodata(np.nan)
_ = test_soil_data_sel.porosity.plot()
# test_soil_data_sel.porosity.attrs # to see info about this variable (unit, fill value, stats, etc.)

# export
test_soil_data_sel.to_netcdf(output_path + "scratch/test_field_soils_onehuc12.nc")

# test out using soil_gnatsgo function
test_basin = pynhd.NLDI().get_basins("11092450")
test_basin_rasterio_wkt = rasterio.crs.CRS.from_wkt(test_basin.crs.to_wkt())
test_basin_geom = test_basin.geometry["USGS-11092450"]
test_soils_data = pygeohydro.soil_properties() # this runs with rasterio warnings but gives result
test_soils_data_mask = pygeoutils.xarray_geomask(test_soil_data, test_basin_geom, test_basin_rasterio_wkt) # this runs fine, without errors
# i kept getting rasterio errors if i used test_basin.crs.to_wkt() here rather than test_basin_rasterio_wkt
test_thickness_data = pygeohydro.soil_gnatsgo("tk0_999a", test_field_geom, test_basin_rasterio_wkt) # this has similar rasterio warnings as above but errors out with more rasterio errors
# test_mukey_data = pygeohydro.soil_gnatsgo("mukey", test_field_geom, field_huc12_bounds.crs)

# try pysda functions
field_huc12_bounds_path = r"C:/Users/sheila.saia/OneDrive - Tetra Tech, Inc/Documents/github/2024-esmc-plet/data/scratch/esmc_test_fields.shp"
test_aoi = sdapoly.shp(field_huc12_bounds_path)
test_properties_available = sdawss.availability()



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


