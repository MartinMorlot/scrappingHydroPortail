import pandas as pd
import geopandas as gpd
from shapely import Point
import json_utility

station_data = json_utility.json_to_python("Correction_station_info_more.json")



for data in station_data:
    coordinates = data['Geometry']['coordinates']
    longitude, latitude = coordinates

    # Create a Shapely Point
    data["shapelyGeom"] = Point(longitude, latitude)



pdData = pd.DataFrame(station_data)

print(pdData.columns)

geodata = gpd.GeoDataFrame(pdData, geometry="shapelyGeom", crs="EPSG:4326")

condition=(geodata['# of data points'] > 15) & (geodata['# of singular years'] > 2) & (geodata['average of data points'] < 0) & ((geodata["# of positive points"] / geodata["# of data points"]) <= 0) & geodata["en_service"]
retained = geodata[condition]

retained.to_file("retained_station_with_correction_more.gpkg", layer="retained_station_with_correction_more.gpkg", driver="GPKG")

geodata["condition"] = condition

geodata['over_15points'] =  geodata['# of data points'] > 15
geodata['over_2years'] = geodata['# of singular years'] > 2
geodata['negative_average'] = geodata['average of data points'] <= 0
geodata["no_postive_points"] = (geodata["# of positive points"] / geodata["# of data points"]) <= 0


geodata.to_file("geodata_station_with_correction_more.gpkg", layer="geodata_station_with_correction_more.gpkg", driver="GPKG")
