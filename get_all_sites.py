import requests
import json

API_url="https://hubeau.eaufrance.fr/api/v2/hydrometrie/referentiel/sites?"

# coordinates, (by default these are all of france)
coord=[-5.1417,41.3719,9.5624,51.0892]

def make_url(API_url, coords=None, size=None, active=None):
    url = API_url
    if(coords):
        if(len(coords)==4):
            coords_map = map(str,coords)
            url += "bbox=" + ",".join(coords_map)

        else:
            raise("Coords not of the right size (needs to be 4)")
    if(size):
        url += "&size={}".format(size)
    if(active):
        url += "&en_service={}".format(active)
    return url

complete_url = make_url(API_url, coord, 9000,1)

response = requests.get(complete_url)

def pretty_json(request_reponse):
    return json.dumps(request_reponse.json(), indent=4)

response_good = pretty_json(response)

with open("all_sites.json", "w") as file:
    file.write(response_good)

complete_url = make_url(API_url, None, 9000,0)

response = requests.get(complete_url)

response_good = pretty_json(response)

with open("all_sites_extra.json", "w") as file:
    file.write(response_good)