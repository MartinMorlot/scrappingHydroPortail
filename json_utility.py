
import json

def json_to_python(file):
    with open(file, "r") as f:
        json_data = f.read()
    json_org_data = json.loads(json_data)
    return json_org_data

def get_data(dict):
    return dict["data"]

def get_info_site(dict, site):
    pass

def get_info_station(dict, station):
    pass