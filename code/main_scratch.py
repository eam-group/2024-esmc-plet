# %% --- header ---

# author: sheila saia
# date created: 2024-07-18
# email: sheila.saia@tetratech.com

# script name: main_scratch.py

# script description: this script does all the plet module data
# analysis.

# notes:


# to do:


# %% ---- load libraries ----
import geopandas as gpd
import pandas as pd
import numpy as np
import os
import sys

# plet module functions
import plet_functions as plet


# %% ---- set paths ----
# project folder path
proj_path = r"C:/Users/sheila.saia/OneDrive - Tetra Tech, Inc/Documents/github/2024-esmc-plet"

# data path
data_path = proj_path + "/data/"

# field data path
field_data_path = data_path + "fields/test_field_file_output2.geojson"

# lookup data path
lookup_data_path = proj_path + "/lookups/"


# %% ---- load data ----
# fields
field_data_raw = gpd.read_file(field_data_path)

# check
# field_data_raw.head
# field_data_raw.columns
# field_data_raw.shape
# field_data_raw.crs # EPSG should be 5070 but it's not

# lookup tables
animal_nutr_lookup = pd.read_csv(str(lookup_data_path + "animal_nutrient_ratio.csv"))
animal_wts_lookup = pd.read_csv(str(lookup_data_path + "animal_wts.csv"))
bmp_eff_lookup = pd.read_csv(str(lookup_data_path + "bmp_eff_vals.csv"))
cn_val_lookup = pd.read_csv(str(lookup_data_path + "cn.csv"))
gw_infil_lookup = pd.read_csv(str(lookup_data_path + "gw_infil_frac.csv"))
gw_nutr_lookup = pd.read_csv(str(lookup_data_path + "gw_nutrients.csv"))
lu_lookup = pd.read_csv(str(lookup_data_path + "lu.csv"))
runoff_nutr_lookup = pd.read_csv(str(lookup_data_path + "runoff_nutrients.csv"))
usle_lookup = pd.read_csv(str(lookup_data_path + "usle.csv"))


# %% ---- scratch calcs -----
# set field data to correct crs
albers_epsg = "EPSG:5070" # albers equal area conic with units of meters
field_data = field_data_raw.set_crs(albers_epsg, allow_override = True)

# check
# field_data.crs
# field_data.columns

# add irrigation columns (hold off!)

# add soil nutrient columns
# insert code to calculate and add columns:
# soil_n_ppm, soil_p_ppm, soil_conc, animal_density

# add tiger columns
# insert code to calculate and add columns:
# state, county, fips

# add nhdplusv2 columns
# insert code to calculate and add columns:
# huc4_num, huc4_name

# add field area
# field_data_albers['area_ac'] = field_data.area / 4046.86 # 1 ac = 4046.36 m

# add prism columns
# insert code to calculate and add columns: 
# aa_rain, r_cor, rd_cor, rain_days, fall_frost, frost_avg

# add usle columns
fips_list = field_data['fips'].unique().astype('float64')
# lu_list = field_data['user_lu'].replace('cropland', 'cropland-cultivated').unique()
usle_lookup_sel = usle_lookup[usle_lookup['fips'].isin(fips_list)].merge(lu_lookup, how = 'left', on = 'land_use').dropna(subset = 'user_lu').reset_index()
usle_lookup_sel_small = usle_lookup_sel.drop(['index', 'name', 'state_name', 'land_use'], axis = 1)
field_data = field_data.merge(usle_lookup_sel_small, how = 'left', on = ['fips', 'user_lu'])



# add soil columns
# insert code to calculate and add columns:
# hsg
