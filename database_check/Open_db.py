import sys, subprocess, os
from io import StringIO
import pandas as pd
from datetime import datetime
import geopandas as gpd
from shapely import Point

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json_utility


VERBOSE = True
def mdb_to_pandas(database_path):
    subprocess.call(["mdb-schema", database_path, "mysql"])
    # Get the list of table names with "mdb-tables"
    table_names = subprocess.Popen(["mdb-tables", "-1", database_path],
                                   stdout=subprocess.PIPE).communicate()[0]
    tables = table_names.splitlines()
    sys.stdout.flush()
    # Dump each table as a stringio using "mdb-export",
    out_tables = {}
    for rtable in tables:
        table = rtable.decode()
        if VERBOSE: print('running table:',table)
        if table != '':
            if VERBOSE: print("Dumping " + table)
            contents = subprocess.Popen(["mdb-export", database_path, table],
                                        stdout=subprocess.PIPE).communicate()[0]
            temp_io = StringIO(contents.decode())
            print(table, temp_io)
            out_tables[table] = pd.read_csv(temp_io)
    return out_tables

# Set up the connection string
# Replace 'path_to_your_file.mdb' with the actual path to your MDB file
mdb_file_path = 'DHMD.MDB'

all_combined = mdb_to_pandas(mdb_file_path)

print(all_combined.keys())

stations = all_combined["station"]
corrections = all_combined["courbecorrection"]

station_data = json_utility.json_to_python("../Correction_station_info_more.json")

station_data_raw = json_utility.json_to_python("../all_stations_extra.json")
site_data_raw = json_utility.json_to_python("../all_sites_extra.json")

station_data_clean = json_utility.get_data(station_data_raw)
site_data_clean = json_utility.get_data(site_data_raw)

all_data_station = []

for nosta in corrections.nosta.unique():
    correction_nosta = corrections[corrections["nosta"] == nosta]
    station = stations[stations["nosta"] == nosta].iloc[0]

    if station.codehydro3 == "K622091001":
        station.codehydro3 = "K622091003"
    station_info = json_utility.get_info_station(station_data_clean, station.codehydro3)
    print(station_info)
    site_info = json_utility.get_info_site(site_data_clean, station.codesitehydro3)
    correction_nosta["ladate"] = pd.to_datetime(correction_nosta["ladate"], format='%m/%d/%y %H:%M:%S')

    file_loc = 'Correction_data_DB/{}.csv'.format(station.codehydro3)

    df_to_write = pd.DataFrame({"date": correction_nosta.ladate, "value": correction_nosta.valeur/100})

    df_to_write = df_to_write.sort_values(by="date")
    
    print(df_to_write)

    df_to_write.to_csv(file_loc,sep=";",header=False, index=False)

    station_dict = {
        "Station": station.codehydro3,
        "Site": station.codesitehydro3,
        "Name_station": station_info["libelle_station"],
        "Surface_bv (km²)": site_info["surface_bv"],
        "Altitude (m)": site_info["altitude_site"],
        "Geometry": site_info["geometry"],
        "en_service": station_info["en_service"],
        "Start Year": str(correction_nosta.ladate.dt.year.min()),
        "End Year": str(correction_nosta.ladate.dt.year.max()),
        "# of data points": correction_nosta.shape[0],
        "# of positive points": correction_nosta.valeur[correction_nosta.valeur > 0].shape[0],
        "average of data points": float(correction_nosta.valeur.mean())/100,
        "# of singular years": len(correction_nosta.ladate.dt.year.unique()),
        "File_location": file_loc,
        "Commentaire": site_info["commentaire_influence_generale_site"]
    }
    
    
    all_data_station.append(station_dict)

json_utility.data_as_json_file(all_data_station, "Correction_station_info_DB.json")

station_data = json_utility.json_to_python("Correction_station_info_DB.json")



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

retained.to_file("retained_station_with_correction_DB.gpkg", layer="retained_station_with_correction_DB.gpkg", driver="GPKG")

geodata["condition"] = condition

geodata['over_15points'] =  geodata['# of data points'] > 15
geodata['over_2years'] = geodata['# of singular years'] > 2
geodata['negative_average'] = geodata['average of data points'] <= 0
geodata["no_postive_points"] = (geodata["# of positive points"] / geodata["# of data points"]) <= 0


geodata.to_file("geodata_station_with_correction_DB.gpkg", layer="geodata_station_with_correction_DB.gpkg", driver="GPKG")



