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
import importlib

# plet module functions
import plet_functions as plet

# reimport for testing plet functions
# importlib.reload(plet)

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


# %% ---- finalize gdf ----
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
# get unique fips values for fields
fips_list = field_data['fips'].unique().astype('float64')

# get subset of usle data based in fips and land use
usle_lookup_sel = (usle_lookup[usle_lookup['fips'].isin(fips_list)]
                               .merge(lu_lookup, how = 'left', on = 'land_use')
                               .dropna(subset = 'user_lu')
                               .reset_index()
                               .drop(['index', 'name', 'state_name', 'land_use'], axis = 1))

# merge with field data
field_data = (field_data
              .merge(usle_lookup_sel, how = 'left', on = ['fips', 'user_lu']))

# check
# field_data.columns

# add cn column
# get unique hsg values for fields
hsg_list = field_data['hsg'].unique()

# rename column so can merge later
cn_val_lookup['user_lu'] =  cn_val_lookup['land_use']

# get subset of cn lookup data based in hsg
cn_val_lookup_sel = (cn_val_lookup[cn_val_lookup['hsg'].isin(hsg_list)]
                       .reset_index()
                       .drop(['index', 'land_use', 'notes'], axis = 1))

# merge with field data
field_data = (field_data
              .merge(cn_val_lookup_sel, how = 'left', on = ['hsg', 'user_lu']))

# check
# field_data.columns
# field_data['cn_value']

# add manure columns
# insert code to calculate and add columns:
# conc, conc_m, 

# add gw infiltration columns
# get unique hsg values for fields
hsg_list = field_data['hsg'].unique()

# rename column so can merge later
gw_infil_lookup['user_lu'] =  gw_infil_lookup['land_use']

# get subset of gw infiltration data based in hsg
gw_infil_lookup_sel = (gw_infil_lookup[gw_infil_lookup['hsg'].isin(hsg_list)]
                       .reset_index()
                       .drop(['index', 'land_use', 'notes'], axis = 1))

# merge with field data
field_data = (field_data
              .merge(gw_infil_lookup_sel, how = 'left', on = ['hsg', 'user_lu']))

# check
# field_data.columns
# field_data['gw_infil_frac']

# add gw columns
# insert code to calculate and add columns: 
# conc_gw

# add bmp efficiency value column
# get unique hsg values for fields
bmp_list = field_data['bmp_name'].unique()

# rename column so can merge later
bmp_eff_lookup['user_lu'] =  bmp_eff_lookup['land_use']

# get subset of bmp eff value lookup data based in bmp_name
bmp_eff_lookup_sel = (bmp_eff_lookup[bmp_eff_lookup['bmp_name'].isin(bmp_list)]
                       .reset_index()
                       .drop(['index', 'bmp_full_name', 'land_use'], axis = 1))

# merge with field data
field_data = (field_data
              .merge(bmp_eff_lookup_sel, how = 'left', on = ['bmp_name', 'user_lu']))

# check
# field_data.columns
# field_data.shape (4 fields, 30 columns)
# field_data['eff_val_nitrogen']

# %% ---- run functions ----
# calculate p
p_gdf = plet.calc_p(field_data)

# check
# p_gdf['p']

# calculate s
s_gdf = plet.calc_s(p_gdf)

# check
# s_gdf['s']

# calculate q
q_gdf = plet.calc_q(s_gdf)

# check
# q_gdf['cn_value']
# q_gdf['q']

# calculate baseline gw infiltration volume
bgwv_gdf = plet.calc_base_gw_v(field_data)

# check
# bgwv_gdf['b_in_v']
