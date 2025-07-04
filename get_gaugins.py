
import json_utility
import time
import os
import gc
import concurrent.futures
from functools import partial

from BrowserDriver import Driver

def check_start_and_wait_for_download(directory, file, button, timeout=300, interval=1):
    dl_start = time.time()
    waiting = True
    files = os.listdir(directory)
    if file in files:
        return True
    button.click()
    while waiting:
        # List all files in the directory
        files = os.listdir(directory)
        # Check if there are any files (assuming the latest file is the downloaded one)
        if file in files:
            waiting = False
            return True
        if time.time() - dl_start > timeout:
            wating = False
            return False
        time.sleep(interval)

def get_gauging(station, download_loc):
    print(station)
    start_time = time.time()
    status = None
    file_to_DL = '{}-Jaugeages.csv'.format(station)
    files = os.listdir(download_loc)
    if file_to_DL in files:
        status = "Downloaded"
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed time: {elapsed_time} seconds")
        return {station: status}

    BrowserViewer = Driver()
    BrowserViewer.options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": download_loc,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
    )
    BrowserViewer.__init__()
    url = 'https://hydro.eaufrance.fr/stationhydro/{}/jaugeages'.format(station)
    BrowserViewer.load_page(url)
    page_loaded = BrowserViewer.get_results()
    if gauging_check in page_loaded:
        BrowserViewer.close_driver()
        del BrowserViewer
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed time: {elapsed_time} seconds")
        return {station: status}
    try:
        conversion_button = BrowserViewer.driver.find_element(BrowserViewer.By.XPATH, '//button[contains(text(), "m³/s")]')
        conversion_button.click()
        download_button = BrowserViewer.driver.find_element(BrowserViewer.By.XPATH, '//button[contains(text(), "Export des données au format CSV")]')
        if check_start_and_wait_for_download(download_loc, file_to_DL, download_button):
            status = "Downloaded"
        BrowserViewer.close_driver()
        del BrowserViewer
        gc.collect()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed time: {elapsed_time} seconds")
        return {station: status}
    except BrowserViewer.NoSuchElementException as e:
        print(f"{station}: {e}")
        BrowserViewer.close_driver()
        del BrowserViewer
        return {station: status}



Gauging_loc = os.path.join(os.getcwd(), 'Gauging_data')


data = json_utility.json_to_python("Correction_station_info_more.json")

stations = [station_info["Station"] for station_info in data]

gauging_check = "L'entité n'a aucun jaugeage."

status_stations = []
max_workers = 15
additional_arg = [Gauging_loc]

# get_gauging(stations[1], Gauging_loc)

with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks to the executor
        futures = [executor.submit(partial(get_gauging, station, Gauging_loc)) for station in stations]

        # As tasks are completed, get their results
        for future in concurrent.futures.as_completed(futures):
            status_stations.append(future.result())

json_utility.data_as_json_file(status_stations, "gauging_download_status.json")
