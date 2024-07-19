import geopandas as gpd
import pandas as pd
import os, random, json
from flask import Flask, request, jsonify

from plet_functions import * 


def PLET(gdf_input):
    ''' This is where we will call specific functions from the other scripts'''
    
    gdf = gpd.GeoDataFrame(gdf_input)
    calc_p(gdf, 'n_animals', 'n_animals', 'n_animals', 'n_animals')
    gdf.to_file(r'E:\Project Work\ESMC\02_Year 2\PLET_buildout\data\test_field_file_output234.geojson')
    
    return gdf