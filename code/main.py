# %% --- header ---

# authors: sheila saia and brian pickard
# date created: 2024-08-02
# emails: sheila.saia@tetratech.com and brian.pickard@tetratech.com

# script name: main.py

# script description: this script provides all calculations
# for the esmc plet module

# notes:


# to do:
# how to reference the lookup tables on the server?
# how to handle multiple types of animals? > current script only considers one animal type (beef cattle)
# how to handle practice change water quanity calcs?
# test other fields


# potential bonus add-ons? (holding off for now):
# how do we handle irrigation water quantity and quality?
# how do we handle gw volume and nutrient load baseline vs practice change calcs? >(hold off?) plet doesn't seem to estimate practice change impact (just baseline) on gw loads
# how do we handle multiple bmps on one field?


# %% --- import libraries ---
# import libraries
import geopandas as gpd
import pandas as pd
import os, random, json
from flask import Flask, request, jsonify

# custom plet functions
import plet_functions as plet


# %% ---- plet module ----
# run plet module
def run_plet(plet_project_path, gdf_epsg="EPSG:5070"):
    """
    description:
    this function performs all plet module functionality for esmc, including:
    input dataset preprocessing, plet module calculations, and export of
    new gdf with all calculations included in new files

    parameters:
        # TODO need to add this information
    returns:
        # TODO need to add this information
    """
    # check function input formats and values
    # TODO add fucticion to run tests

    # define project folder path
    proj_path = plet_project_path

    # define data path
    data_path = proj_path + "/data/"

    # define lookup data path
    lookup_path = proj_path + "/lookups/"

    # define input field data path
    input_data_path = data_path + "fields/test_field_file_output2.geojson"
    # TODO need to fix these paths for app functionality (ask b)

    # define output data path
    output_data_path = data_path + "fields/"
    # TODO need to fix these paths for app functionality (ask b)

    # input field data
    field_gdf_raw = gpd.read_file(input_data_path)

    # set data to correct crs
    field_gdf = field_gdf_raw.set_crs(gdf_epsg, allow_override=True)

    # check gdf formats and values provided by the user
    # TODO add fucticion to run tests

    # load lookup tables
    animal_nutr_lookup = pd.read_csv(str(lookup_path + "animal_nutrient_ratio.csv"))
    animal_wts_lookup = pd.read_csv(str(lookup_path + "animal_wts.csv"))
    bmp_eff_lookup = pd.read_csv(str(lookup_path + "bmp_eff_vals.csv"))
    cn_val_lookup = pd.read_csv(str(lookup_path + "cn.csv"))
    gw_infil_lookup = pd.read_csv(str(lookup_path + "gw_infil_frac.csv"))
    gw_nutr_lookup = pd.read_csv(str(lookup_path + "gw_nutrients.csv"))
    lu_lookup = pd.read_csv(str(lookup_path + "lu.csv"))
    runoff_nutr_lookup = pd.read_csv(str(lookup_path + "runoff_nutrients.csv"))
    usle_lookup = pd.read_csv(str(lookup_path + "usle.csv"))

    # append nass/soil nutrient columns
    # TODO insert code to calculate and add columns:
    # soil_n_ppm, soil_p_ppm, soil_conc, animal_density

    # append tiger columns
    # TODO insert code to calculate and add columns:
    # state, county, fips

    # append nhdplusv2 columns
    # TODO insert code to calculate and add columns:
    # huc4_num, huc4_name

    # append field area calculation
    field_gdf["area_ac"] = field_gdf.area / 4046.86
    # conversion factor used: 1 ac = 4046.36 m

    # append prism columns
    # TODO insert code to calculate and add columns:
    # aa_rain, r_cor, rd_cor, rain_days, fall_frost, frost_avg

    # append usle columns
    # TODO get unique fips values for fields
    fips_list = field_gdf["fips"].unique().astype("float64")
    # get subset of usle data based in fips and land use
    usle_lookup_sel = (
        usle_lookup[usle_lookup["fips"].isin(fips_list)]
        .merge(lu_lookup, how="left", on="land_use")
        .dropna(subset="user_lu")
        .reset_index()
        .drop(["index", "name", "state_name", "land_use"], axis=1)
    )
    # merge usle data with field data
    field_gdf_usle = field_gdf.merge(
        usle_lookup_sel, how="left", on=["fips", "user_lu"]
    )

    # append cn value column
    # get unique hsg values for fields
    hsg_list = field_gdf_usle["hsg"].unique()
    # rename column so can merge later
    cn_val_lookup["user_lu"] = cn_val_lookup["land_use"]
    # get subset of cn lookup data based in hsg
    cn_val_lookup_sel = (
        cn_val_lookup[cn_val_lookup["hsg"].isin(hsg_list)]
        .reset_index()
        .drop(["index", "land_use", "notes"], axis=1)
    )
    # merge with field data
    field_gdf_cn = field_gdf_usle.merge(
        cn_val_lookup_sel, how="left", on=["hsg", "user_lu"]
    )

    # append animal stats columns
    field_gdf_ani = plet.calc_animal_stats(field_gdf_cn, animal_type="beef_cattle")

    # append manure columns
    # get unique lu values for fields
    inten_list = field_gdf_ani["animal_inten"].unique()
    # rename column so can merge later
    runoff_nutr_lookup["user_lu"] = runoff_nutr_lookup["land_use"]
    # get subset of gw infiltration data based in hsg
    runoff_nutr_lookup_sel = (
        runoff_nutr_lookup[runoff_nutr_lookup["animal_inten"].isin(inten_list)]
        .reset_index()
        .drop(["index", "land_use"], axis=1)
    )
    # merge with field data
    field_gdf_man = field_gdf_ani.merge(
        runoff_nutr_lookup_sel, how="left", on=["user_lu", "animal_inten"]
    )

    # append bmp efficiency value column
    # get unique hsg values for fields
    bmp_list = field_gdf_man["bmp_name"].unique()
    # rename column so can merge later
    bmp_eff_lookup["user_lu"] = bmp_eff_lookup["land_use"]
    # get subset of bmp eff value lookup data based in bmp_name
    bmp_eff_lookup_sel = (
        bmp_eff_lookup[bmp_eff_lookup["bmp_name"].isin(bmp_list)]
        .reset_index()
        .drop(["index", "bmp_full_name", "land_use"], axis=1)
    )
    # merge with field data
    field_gdf_bmp = field_gdf_man.merge(
        bmp_eff_lookup_sel, how="left", on=["bmp_name", "user_lu"]
    )

    # calculate p

    # calculate s

    # calculate q

    # calculate baseline runoff volume

    # calculate baseline runoff nutrient load (for n and p)

    # calculate sediment loss from uniform erosion

    # calculate baseline runoff sediment load

    # calculate practice change runoff volume

    # calculate practice change sediment-bound nutrient load

    # calculate practice change runoff nutrient load (for n and p)

    # calculate practice change runoff sediment load

    # calculate percent change

    # export

    # return
    return gdf

    # notes from b
    # gdf = gpd.GeoDataFrame(gdf_input))
    # calc_p(gdf, 'n_animals', 'n_animals', 'n_animals', 'n_animals')
    # gdf.to_file(r'E:\Project Work\ESMC\02_Year 2\PLET_buildout\data\test_field_file_output234.geojson')
