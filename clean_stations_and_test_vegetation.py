import time
import concurrent.futures
import os
import gc

from BrowserDriver import Driver
from json_utility import json_to_python


all_data = json_to_python("all_stations_extra.json")

# station_with_department = [i for i in all_data["data"] if i["code_departement"]]

station_with_department = [i for i in all_data["data"]]

#print(station_with_department)

stations_code = {station["code_station"] for station in station_with_department}

correction_check_string = "Cette station n'a pas encore de courbe de correction."

correction_check = "Courbes - Jaugeages"



stations_with_corection = set()

def station_check(station_code_unique):
    BrowserViewer = None
    # Record the start time
    start_time = time.time()
    print(station_code_unique)
    html_file = "all_pages/{}.html".format(station_code_unique)
    if not os.path.exists(html_file):
        BrowserViewer = Driver()
        url = 'https://hydro.eaufrance.fr/stationhydro/{}/courbe-correction'.format(station_code_unique)
        print("Get correction page")
        BrowserViewer.load_page(url)
        results = BrowserViewer.get_results()
        with open(html_file, "w") as file:
            file.write(results)
    else:
            print("File already exists!")

    with open(html_file, "r") as file:
            results = file.read()

    if (not correction_check in results) or correction_check_string in results:
        print("No Correction!")
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed time: {elapsed_time} seconds")
        if BrowserViewer:
            BrowserViewer.close_driver()
            del BrowserViewer
            gc.collect()
        return "No Correction!"
    
    correction_file = "correction_page/{}.html".format(station_code_unique)

    with open(correction_file, "w") as file:
            file.write(results)

    stations_with_corection.add(station_code_unique)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")
    if BrowserViewer:
        BrowserViewer.close_driver()
        del BrowserViewer
        gc.collect()
    return station_code_unique



max_workers = 15


with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks to the executor
        futures = [executor.submit(station_check, station_code_unique) for station_code_unique in stations_code]

        # As tasks are completed, get their results
        for future in concurrent.futures.as_completed(futures):
            print(future.result())

with open("station_with_correction_more.csv",  "w") as file:
    for station in stations_with_corection:
        file.writelines(station+"\n")