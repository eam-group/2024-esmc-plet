import geopandas as gpd
import requests
import os

def download_prism_data(year, output_dir):
    """
    Download PRISM 30-year precipitation annual normals for a specified year.
    
    :param year: The year for which to download the PRISM data.
    :param output_dir: Directory to save the downloaded file.
    """
    base_url = "https://services.nacse.org/prism/data/public/normals/4km"
    variable = "ppt"  # Precipitation
    interval = '14'

    url = f"{base_url}/{variable}/{interval}"

    response = requests.get(url)
    if response.status_code == 200:
        file_name = f"PRISM_{variable}_{interval}_{year}.zip"
        file_path = os.path.join(output_dir, file_name)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded PRISM data for year {year} to {file_path}")
    else:
        print(f"Failed to download PRISM data for year {year}. Status code: {response.status_code}")

def process_geodataframe(gdf, output_dir):
    """
    Process GeoDataFrame and download PRISM data for each unique year.
    
    :param gdf: GeoDataFrame containing a 'year' column.
    :param output_dir: Directory to save downloaded PRISM data files.
    """
    if 'year' not in gdf.columns:
        raise ValueError("GeoDataFrame must contain a 'year' column")

    unique_years = gdf['year'].unique()
    for year in unique_years:
        download_prism_data(year, output_dir)

# Example usage
gdf = gpd.read_file(r'C:\temp\ESMC_test.geojson')
output_directory = r'C:\temp\ESMC'
process_geodataframe(gdf, output_directory)