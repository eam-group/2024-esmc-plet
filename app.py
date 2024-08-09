# %% --- header ---

# author: brian pickard and sheila saia
# date created: 2024-07-05
# email: brian.pickard@tetratech.com and sheila.saia@tetratech.com

# script name: flask_app.py

# script description: this script contains the code required to run the
# plet module flask app

# notes:


# to do:


# %% ---- flask app ----
# import libraries
from flask import Flask, request, jsonify, make_response
import geopandas as gpd
import os
import sys
import json

# custom plet functions
import plet_functions as plet

# set up the flask app
app = Flask(__name__)

# direct the request
# allows for post (initial geojson request) and get (updated geojson response)
@app.route('/result', methods = ['POST', 'GET'])

# define the app functions
def result():
    # save the current state of sys.stdout
    old_stdout = sys.stdout

    # open log file for saving print statements to
    log_file = open("message.log", "w")

    # define sys.stdout
    sys.stdout = log_file

    # get the request
    data = request.get_json()   

    # convert geojson to geopandas df
    gdf = gpd.GeoDataFrame.from_features(data["features"])

    # run plet module
    plet_result = plet.run_plet(gdf)
    # TODO update this based on plet module inputs
    
    # convert plet output from geopandas df to geojson
    plet_result = plet_result.to_json()

    # convert geojson to dictionary
    plet_result_dict = json.loads(plet_result)
    # TODO check that this is what austin wants > maybe he wants the geojson instead?
    # TODO check if this step is needed? can't just put run_plet into jsonify()?

    # define the response
    response = make_response(jsonify(plet_result_dict), 200) # sms edited
    
    # reset to the initial state of std.out
    sys.stdout = old_stdout

    # close the log file
    log_file.close()

    # return
    return response

# if script is run directly (i.e., __name__ is set to __main__)
# run it in debug mode
if __name__ == '__main__':
    # define the port
    app_port = int(os.environ.get('PORT', 8080)) # sms added

    # start web app server/run the app in debug mode
    app.run(debug=True, host='0.0.0.0', port=app_port) # sms edited host and port