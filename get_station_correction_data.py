import gc
from datetime import datetime
import time
import concurrent.futures

import json_utility
from BrowserDriver import Driver


all_stations = []
with open("station_with_correction_more.csv", "r") as file:
    for line in file:
        station = line.strip()
        all_stations.append(station)


station_data_raw = json_utility.json_to_python("all_stations_extra.json")
site_data_raw = json_utility.json_to_python("all_sites_extra.json")

station_data_clean = json_utility.get_data(station_data_raw)
site_data_clean = json_utility.get_data(site_data_raw)

station_test = all_stations[0]

def get_corrections_and_data(station_test):
    start_time = time.time()
    BrowserViewer = Driver()
    url = 'https://hydro.eaufrance.fr/stationhydro/{}/courbe-correction'.format(station_test)
    print("Get correction page")
    BrowserViewer.load_page(url)

    data = []
    while True:
        rows = BrowserViewer.driver.find_elements(BrowserViewer.By.CSS_SELECTOR, 'table tbody tr')
        for row in rows:
            # Extract data from each row and store it
            cols = row.find_elements(BrowserViewer.By.CSS_SELECTOR, 'td')
            data.append([col.get_attribute("textContent").strip()  for col in cols])

        #li.page-item:nth-child(8)
        # Try to click the "Next" button
        try:
            next_button = BrowserViewer.driver.find_element(BrowserViewer.By.XPATH, "//li[contains(@class, 'page-item') and contains(@title, 'next page')]/a")
            next_button.click()
        except BrowserViewer.NoSuchElementException:
            # Exit the loop if the "Next" button is not found
            break

    BrowserViewer.close_driver()
    del BrowserViewer
    gc.collect()

    startY= 3000
    endY= 0
    indY=set()
    dataPoint = 0
    file_loc = 'Correction_data/{}.csv'.format(station_test)
    total_corth = 0
    positive = 0
    with open(file_loc, "w") as file:
        for data_point in data:
            if len(data_point) == 2:
                if len(data_point[1]) > 0:
                    try:
                        date = datetime.strptime(data_point[0], "%d/%m/%Y %H:%M")
                        year = date.year
                        value=float(data_point[1].replace(",","."))
                        line = "{};{}\n".format(date,value)
                        file.write(line)
                        dataPoint += 1
                        if year < startY:
                            startY = year
                        if year > endY:
                            endY = year
                        indY.add(year)
                        total_corth += value
                        if value > 0:
                            positive += 1
                    except ValueError as ve:
                        raise ValueError(f"Invalid value provided for station {station_test}: {ve}")



    indYnb = len(indY)

    station_info = json_utility.get_info_station(station_data_clean, station_test)

    site_code = station_info["code_site"]

    site_info = json_utility.get_info_site(site_data_clean, site_code)

    datamean = None
    if dataPoint:
        datamean = total_corth / dataPoint

    station_dict = {
        "Station": station_test,
        "Site": site_code,
        "Name_station": station_info["libelle_station"],
        "Surface_bv (km²)": site_info["surface_bv"],
        "Altitude (m)": site_info["altitude_site"],
        "Geometry": site_info["geometry"],
        "en_service": station_info["en_service"],
        "Start Year": startY,
        "End Year": endY,
        "# of data points": dataPoint,
        "# of positive points": positive,
        "average of data points": datamean,
        "# of singular years": indYnb,
        "File_location": file_loc,
        "Commentaire": site_info["commentaire_influence_generale_site"]
    }

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")

    return station_dict


# print(get_corrections_and_data("A623201001"))

all_data_station = []
max_workers = 15

with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks to the executor
        futures = [executor.submit(get_corrections_and_data, station_code_unique) for station_code_unique in all_stations]

        # As tasks are completed, get their results
        for future in concurrent.futures.as_completed(futures):
            all_data_station.append(future.result())

json_utility.data_as_json_file(all_data_station, "Correction_station_info_more.json")




            

