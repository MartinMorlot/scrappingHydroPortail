
import json

def json_to_python(file):
    with open(file, "r") as f:
        json_data = f.read()
    json_org_data = json.loads(json_data)
    return json_org_data

def get_data(dict):
    return dict["data"]

def get_info_site(list_sites, site):
    site_found = [element for element in list_sites if element["code_site"] == site]
    if len(site_found) == 0:
        return
    return site_found[0]

def get_info_station(list_stations, station):
    station_found = [element for element in list_stations if element["code_station"] == station]
    if len(station_found) == 0:
        return
    return station_found[0]

def data_as_json_file(data, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    return "written"