from BrowserDriver import Driver
import gc
from datetime import datetime
import json_utility

all_stations = []
with open("station_with_correction.csv", "r") as file:
    for line in file:
        station = line.strip()
        all_stations.append(station)


station_test = all_stations[0]

print(station_test)

BrowserViewer = Driver()
url = 'https://hydro.eaufrance.fr/stationhydro/{}/courbe-correction'.format(station_test)
print("Get correction page")
BrowserViewer.load_page(url)

data = []
while True:
    rows = BrowserViewer.driver.find_elements(BrowserViewer.By.CSS_SELECTOR, 'table tr')
    for row in rows:
        # Extract data from each row and store it
        cols = row.find_elements(BrowserViewer.By.TAG_NAME, 'td')
        data.append([col.text for col in cols])
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
with open(file_loc, "w") as file:
    for data_point in data:
        if len(data_point) == 2:
            year = datetime.strptime(data_point[0], "%d/%m/%Y %H:%M").year
            line = "{}, {} \n".format(data_point[0], data_point[1])
            file.write(line)
            dataPoint += 1
            if year < startY:
                startY = year
            if year > endY:
                endY = year
            indY.add(year)
indYnb = len(indY)

station_dict = {
    "Station": station_test,
    "Start Year": startY,
    "End Year": endY,
    "# of data points": dataPoint,
    "# of singular years": indYnb,
    "File_location": file_loc
} 

print(station_dict)



            

