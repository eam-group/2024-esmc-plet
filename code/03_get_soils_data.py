# %% --- header ---

# author:
# date created:
# email:

# script name: 03_get_soils_data.py

# script description: this script gets soils property (including usle 
# information) to run the plet module calculations

# to do:


# %% --- set up ---

# import libraries
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
import os
import sys
import math
import us

# get ssurgo functions
pysda_library_path = r"C:/Users/sheila.saia/OneDrive - Tetra Tech, Inc/Documents/github/2024-esmc-plet/functions/pysda"
sys.path.append(pysda_library_path)
import sdapoly, sdaprop #, sdainterp, sdawss
# help: https://github.com/ncss-tech/pysda

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


# %% ---- get huc12 bounds for state ----
# get state bounds for field_state
# help: https://pypi.org/project/us/

# field data location from esmc (this is test data for now)
field_state = "IL"
# this we should pull from the mmrv json file

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
# this works!

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


# test out pygeohydro library (couldn't get this to work but my environment was probably not set up correctly)
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
 
