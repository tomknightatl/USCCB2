from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

# Specify the path to chromedriver for Raspberry Pi (ARM)
webdriver_service = Service('/usr/bin/chromedriver')
driver = webdriver.Chrome(service=webdriver_service)

try:
    driver.get("https://www.google.com")
    print("Successfully opened Google!")
    time.sleep(3) # Wait for 3 seconds to see the browser
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    driver.quit() # Close the browser
