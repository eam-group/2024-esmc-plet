# %% --- header ---

# author: sheila saia
# date created: 2024-07-18
# email: sheila.saia@tetratech.com

# script name: main_scratch.py

# script description: this script does all the plet module data
# analysis.

# notes:


# to do:
# how to handle multiple types of animals? > current script only considers one animal type (beef cattle)
# how to handle practice change water quanity calcs?
# test other fields


# potential bonus add-ons? (holding off for now):
# how do we handle irrigation water quantity and quality?
# how do we handle gw volume and nutrient load baseline vs practice change calcs? >(hold off?) plet doesn't seem to estimate practice change impact (just baseline) on gw loads
# how do we handle multiple bmps on one field?


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
proj_path = (
    r"C:/Users/sheila.saia/OneDrive - Tetra Tech, Inc/Documents/github/2024-esmc-plet"
)

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
albers_epsg = "EPSG:5070"  # albers equal area conic with units of meters
field_data = field_data_raw.set_crs(albers_epsg, allow_override=True)

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
# field_data_area['area_ac'] = field_data.area / 4046.86 # 1 ac = 4046.36 m
field_data_area = field_data # for now

# add prism columns
# insert code to calculate and add columns:
# aa_rain, r_cor, rd_cor, rain_days, fall_frost, frost_avg

# add usle columns
# get unique fips values for fields
fips_list = field_data_area["fips"].unique().astype("float64")

# get subset of usle data based in fips and land use
usle_lookup_sel = (
    usle_lookup[usle_lookup["fips"].isin(fips_list)]
    .merge(lu_lookup, how="left", on="land_use")
    .dropna(subset="user_lu")
    .reset_index()
    .drop(["index", "name", "state_name", "land_use"], axis=1)
)

# merge with field data
field_data_usle = field_data_area.merge(usle_lookup_sel, how="left", on=["fips", "user_lu"])

# check
# field_data_usle.columns

# add cn column
# get unique hsg values for fields
hsg_list = field_data_usle["hsg"].unique()

# rename column so can merge later
cn_val_lookup["user_lu"] = cn_val_lookup["land_use"]

# get subset of cn lookup data based in hsg
cn_val_lookup_sel = (
    cn_val_lookup[cn_val_lookup["hsg"].isin(hsg_list)]
    .reset_index()
    .drop(["index", "land_use", "notes"], axis=1)
)

# merge with field data
field_data_cn = field_data_usle.merge(
    cn_val_lookup_sel, how="left", on=["hsg", "user_lu"]
)

# check
# field_data_cn.columns
# field_data_cn['cn_value']

# add animal stats columns
field_data_ani = plet.calc_animal_stats(field_data_cn, animal_type="beef_cattle")

# check
# field_data_ani.columns
# field_data_ani['animal_den']
# field_data_ani['animal_inten']

# add manure columns
# get unique lu values for fields
inten_list = field_data_ani["animal_inten"].unique()

# rename column so can merge later
runoff_nutr_lookup["user_lu"] = runoff_nutr_lookup["land_use"]

# get subset of gw infiltration data based in hsg
runoff_nutr_lookup_sel = (
    runoff_nutr_lookup[runoff_nutr_lookup["animal_inten"].isin(inten_list)]
    .reset_index()
    .drop(["index", "land_use"], axis=1)
)

# merge with field data
field_data_man = field_data_ani.merge(
    runoff_nutr_lookup_sel, how="left", on=["user_lu", "animal_inten"]
)

# check
# field_data_man.columns

# add gw infiltration columns
# rename column so can merge later
gw_infil_lookup["user_lu"] = gw_infil_lookup["land_use"]

# get subset of gw infiltration data based in hsg
gw_infil_lookup_sel = (
    gw_infil_lookup[gw_infil_lookup["hsg"].isin(hsg_list)]
    .reset_index()
    .drop(["index", "land_use", "notes"], axis=1)
)

# merge with field data
field_data_inf = field_data_man.merge(
    gw_infil_lookup_sel, how="left", on=["hsg", "user_lu"]
)

# check
# field_data_inf.columns
# field_data_inf['gw_infil_frac']

# add gw columns
# insert code to calculate and add columns:
# conc_gw
field_data_gw = field_data_inf  # for now
# TODO fix this

# add bmp efficiency value column
# get unique hsg values for fields
bmp_list = field_data_gw["bmp_name"].unique()

# rename column so can merge later
bmp_eff_lookup["user_lu"] = bmp_eff_lookup["land_use"]

# get subset of bmp eff value lookup data based in bmp_name
bmp_eff_lookup_sel = (
    bmp_eff_lookup[bmp_eff_lookup["bmp_name"].isin(bmp_list)]
    .reset_index()
    .drop(["index", "bmp_full_name", "land_use"], axis=1)
)

# merge with field data
field_data_bmp = field_data_gw.merge(
    bmp_eff_lookup_sel, how="left", on=["bmp_name", "user_lu"]
)

# check
# field_data_bmp.columns
# field_data_bmp.shape (4 fields, 30 columns)
# field_data_bmp['eff_val_nitrogen']

# %% ---- run functions ----
# calculate p
p_gdf = plet.calc_p(field_data_bmp)

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

# calculate baseline runoff volume
brunv_gdf = plet.calc_base_run_v(q_gdf)

# check
# brunv_gdf['b_run_v']

# calculate baseline gw infiltration volume
# bgwv_gdf = plet.calc_base_gw_v(brunv_gdf)
# hold off on this for now

# check
# bgwv_gdf['b_in_v']

# calculate baseline runoff nutrient load (for n and p)
brunl_gdf = plet.calc_base_run_nl(brunv_gdf)

# check
# brunl_gdf.columns
# brun1_gdf['b_run_n']
# brun1_gdf['b_run_p']

# calculate sediment loss from uniform erosion
e_gdf = plet.calc_e(brunl_gdf)

# check
# e_gdf['erosion']

# calculate baseline runoff sediment load
bruns_gdf = plet.calc_base_run_sl(e_gdf)

# check
# bruns_gdf.columns
# bruns_gdf['del_ratio']
# bruns_gdf['b_run_sl']

# calculate practice change runoff volume
prunv_gdf = plet.calc_prac_run_v(bruns_gdf)

# check
# prunv_gdf.columns
# prunv_gdf['p_run_v']

# calculate practice change sediment-bound nutrient load
psed_gdf = plet.calc_prac_sed_nl(prunv_gdf)

# check
# psed_gdf.columns

# calculate practice change runoff nutrient load
prunl_gdf = plet.calc_prac_run_nl(psed_gdf)

# check
# prunl_gdf.columns
# prunl_gdf['p_run_n']
# prunl_gdf['p_run_p']

# calculate practice change runoff sediment load
pruns_gdf = plet.calc_prac_run_sl(prunl_gdf)

# check
# pruns_gdf.columns
# pruns_gdf['p_run_s']


# calculate percent change
gdf_final = plet.calc_perc_change(pruns_gdf)

# export to check
df_final = pd.DataFrame(gdf_final)
df_final.to_csv(proj_path + "/data/scratch/plet_output_test.csv")

# check
# gdf_final.columns
# gdf_final['pc_v']
# gdf_final['pc_n']
# gdf_final['pc_p']
# gdf_final['del_ratio']
# gdf_final['erosion']
# gdf_final['area_ac']
# gdf_final['b_run_s']
# gdf_final['pc_s']

# check field 1
# del_ratio matches stepl
# erosion matches stepl
# b_run_s matches stepl
# p_run_s matches stepl
# p matches stepl
# q matches stepl
# b_run_v matches stepl
# b_in_v matches stepl
# b_run_n matches stepl
# conc_n, conc_nm, conc_p, conc_mp all match stepl
# p_run_n matches stepl
# b_run_p matches stepl
# p_run_p matches stepl

# check field 4
