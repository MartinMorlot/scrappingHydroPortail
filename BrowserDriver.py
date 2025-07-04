from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

class Driver():
    # Specify the path to your ChromeDriver
    driver_path = 'chromedriver-linux64/chromedriver'  # You need to download this and provide the path
    By = By
    NoSuchElementException = NoSuchElementException
    options = None
    
    
    def __init__(self):
        # Set up the headless browser
        if not self.options:
            self.options = Options()
            self.options.add_argument("--headless")  # Run in headless mode, without opening a browser window
            self.options.add_argument("--disable-gpu")
            self.options.add_argument("--window-size=1920x1080")

        # Create a Service object
        self.service = Service(executable_path=self.driver_path)

        # Initialize the driver
        self.driver = webdriver.Chrome(options=self.options, service=self.service)
    
    def close_driver(self):
        self.driver.quit()

    def reinitialize(self):
        self.driver = webdriver.Chrome(options=self.options, service=self.service)
    
    def load_page(self, url):
        self.driver.get(url)
    
    def get_results(self):
        return self.driver.page_source