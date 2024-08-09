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
# how to handle multiple types of animals? > current script only
# considersone animal type (beef cattle)
# how to handle practice change water quanity calcs?
# check that plet module values match stepl values
# send all messages to stdout

# potential bonus add-ons (holding off for now):
# how do we handle irrigation water quantity and quality?
# how do we handle gw infiltration volume and gw nutrient load
# baseline vs practice change calcs? > (hold off?) plet doesn't seem to
# estimate practice change impact (just baseline) on gw loads
# how do we handle multiple bmps on one field?


# %% --- import libraries ---
# import libraries
import geopandas as gpd
import pandas as pd
import numpy as np
import os, random, json, sys, importlib
from flask import Flask, request, jsonify

# custom plet functions
from run_plet import run_plet
from append_lookups import append_lookups

# reimport for testing plet functions
# importlib.reload(plet)


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

    # define data path
    data_path = plet_project_path + "/data/"

    # define lookup data path
    lookup_path = plet_project_path + "/lookups/"

    # define input field data path
    input_data_path = data_path + "fields/test_field_file_output2.geojson"
    # TODO need to fix these paths for app functionality (ask b)

    # define output data path
    output_data_gdf_path = data_path + "scratch/test_plet_output.geojson"
    output_data_df_path = data_path + "scratch/test_plet_output.csv"
    # TODO need to fix these paths for app functionality (ask b)

    # input field data
    field_gdf_raw = gpd.read_file(input_data_path)

    # set data to correct crs
    field_gdf = field_gdf_raw.set_crs(gdf_epsg, allow_override=True)

    # check gdf formats and values provided by the user
    # TODO add fucticion to run error handling

    # append tiger (county/state) columns
    # TODO insert code to calculate and add columns:
    # state, county, fips

    # append nhdplusv2 columns (use v2 so is compatible with sparrow)
    # TODO insert code to calculate and add columns:
    # huc4_num, huc4_name

    # append field area calculation
    # field_gdf["area_ac"] = field_gdf.area / 4046.86
    # conversion factor used: 1 ac = 4046.36 m
    # TODO uncomment this to test it

    # append soil columns
    # TODO insert code to calculate and add columns:
    # hgs, soil_n_ppm (optional), soil_p_ppm (optional), soil_conc (optional)

    # append nass columns
    # TODO insert code to calculate and add columns:
    # n_animal, (type_animal?), animal_density

    # append prism columns
    # TODO insert code to calculate and add columns:
    # aa_rain, r_cor, rd_cor, rain_days, fall_frost, frost_avg


    # TODO is it better to just overwrite/append in the code below,
    # rather than redefining each time (or maybe it doesn't matter?)
    # (ask b)

    # append lookups
    field_gdf = append_lookups(field_gdf)

    # run plet
    field_gdf = run_plet(field_gdf)

    # export
    field_gdf.to_file(output_data_gdf_path)

    # export (for testing only)
    field_df = pd.DataFrame(field_gdf)
    field_df.to_csv(output_data_df_path)

    # return
    return field_gdf

# test
# proj_path = (
#     r"C:/Users/sheila.saia/OneDrive - Tetra Tech, Inc/Documents/github/2024-esmc-plet"
# )
# test_gdf = run_plet(plet_project_path=proj_path)
# export of geojson and csv worked
# TODO check why i can't set the espg without getting an error