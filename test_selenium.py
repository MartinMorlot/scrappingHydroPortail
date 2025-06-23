from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Set up the headless browser
options = Options()
options.add_argument("--headless")  # Run in headless mode, without opening a browser window
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")

# Specify the path to your ChromeDriver
driver_path = 'chromedriver-linux64/chromedriver'  # You need to download this and provide the path

# Create a Service object
service = Service(executable_path=driver_path)


# Initialize the driver
driver = webdriver.Chrome(options=options, service=service)

# Load the webpage
url = 'https://hydro.eaufrance.fr/stationhydro/K055001010/courbe-correction'
driver.get(url)

# At this point, the page is fully loaded, including JavaScript
# You can access the page source with driver.page_source

print(driver.page_source)

# Don't forget to close the driver
driver.quit()