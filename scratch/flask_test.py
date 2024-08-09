import requests
import json
import geopandas as gpd

geojson_file_path = r'E:\Project Work\ESMC\02_Year 2\PLET_buildout\data\test_field_file.geojson'
output_file_path = r'E:\Project Work\ESMC\02_Year 2\PLET_buildout\data\test_field_file_output234.geojson'

# Read the GeoJSON data from the file
with open(geojson_file_path, 'r') as file:
    geojson_data = json.load(file)


# Define the URL of the local Flask app
url = 'http://127.0.0.1:2000/result'

# Send the POST request with the GeoJSON data
response = requests.post(url, json=geojson_data)

## Check if the response was successful
if response.status_code == 200:
    modified_geojson_data = response.json()
    
    # Write the modified GeoJSON data to a new file
    with open(output_file_path, 'w') as outfile:
        json.dump(modified_geojson_data, outfile, indent=4)
    
    print(f"Modified GeoJSON saved to {output_file_path}")
else:
    print(f"Failed to receive modified GeoJSON. Status Code: {response.status_code}")
    print(f"Response: {response.text}")