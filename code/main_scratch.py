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
runoff_nutr_lookup = pd.read_csv(str(lookup_data_path + "runoff_nutrients.csv"))


# %% ---- scratch calcs -----
# set field data to correct crs
albers_epsg = "EPSG:5070" # albers equal area conic with units of meters
field_data = field_data_raw.set_crs(albers_epsg, allow_override = True)

# check
# field_data.crs
# type(field_data['area_ac'][0]) # int
# type(field_data['n_months'][0]) # int
# type(field_data['m_area_ac'][0]) # float
# type(field_data['n_animals'][0]) # int
# type(field_data['bmp_name'][0]) # str
# type(field_data['bmp_ac'][0]) # float

# calculate field area
# field_data_albers['area_acres'] = field_data.area / 4046.86 # 1 ac = 4046.36 m

