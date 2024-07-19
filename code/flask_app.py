from flask import Flask, request, jsonify
import geopandas as gpd
import json
from main import PLET
app = Flask(__name__)


@app.route('/result', methods = ['POST', 'GET'])

def result():

    data = request.get_json()   
    gdf = gpd.GeoDataFrame.from_features(data["features"])
    runall = PLET(gdf)
    
    runall = runall.to_json()
    runall_dict = json.loads(runall)
    
    return jsonify(runall_dict), 200

if __name__ == '__main__':
    app.run(debug=True, port=2000)
    
