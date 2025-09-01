import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import traceback

# --- Configuration ---
DATABASE_PATH = 'dioceses.db'
TARGET_URL = 'https://archatl.com/parishes/find-a-parish/'
# Ensure chromedriver is in your PATH or specify its path here
# CHROME_DRIVER_PATH = '/path/to/your/chromedriver' # Uncomment and set if not in PATH

# --- Database Setup ---
def setup_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Parishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            phone TEXT,
            fax TEXT,
            website TEXT,
            source_url TEXT,
            extraction_datetime TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_parish_data(parish_data):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Parishes (name, address, phone, fax, website, source_url, extraction_datetime)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        parish_data['name'],
        parish_data['address'],
        parish_data['phone'],
        parish_data['fax'],
        parish_data['website'],
        parish_data['source_url'],
        parish_data['extraction_datetime']
    ))
    conn.commit()
    conn.close()

# --- Web Scraping Logic ---
def scrape_parishes():
    setup_database()

    # Initialize WebDriver
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') # Uncomment to run in headless mode (no browser UI)
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    # Ensure chromedriver is in your PATH or specify its path here
    # CHROME_DRIVER_PATH = '/path/to/your/chromedriver' # Uncomment and set if not in PATH
    webdriver_service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=webdriver_service, options=options)

    driver.get(TARGET_URL)
    wait = WebDriverWait(driver, 60) # Increased wait time for dynamic content

    processed_parishes = set() # To keep track of already processed parishes and avoid duplicates

    while True:
        try:
            # Wait for parish list to load
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.corePrettyStyle > a > span')))

            parish_elements = driver.find_elements(By.CSS_SELECTOR, 'li.corePrettyStyle > a > span')
            current_page_parish_names = [elem.text for elem in parish_elements]

            for i in range(len(parish_elements)):
                # Re-find elements in case DOM changed after a click
                parish_elements = driver.find_elements(By.CSS_SELECTOR, 'li.corePrettyStyle > a > span')
                parish_name_elem = parish_elements[i]
                parish_name = parish_name_elem.text

                if parish_name in processed_parishes:
                    continue # Skip if already processed

                print(f"Processing parish: {parish_name}")

                try:
                    # Click on the parish name to reveal details
                    # Use JavaScript click if direct click fails
                    # Click on the parent <a> element to reveal details
                    clickable_element = parish_name_elem.find_element(By.XPATH, './parent::a')
                    driver.execute_script("arguments[0].click();", clickable_element)

                    # Wait for the details to appear in the info window
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.gm-style-iw-d')))

                    info_window = driver.find_element(By.CSS_SELECTOR, 'div.gm-style-iw-d')

                    address = ""
                    phone = ""
                    fax = ""
                    website = ""

                    # Extract address (usually in a <p> tag or similar)
                    try:
                        address_elem = info_window.find_element(By.XPATH, './/p[contains(text(), "Address:")]')
                        address = address_elem.text.replace("Address:", "").strip()
                    except:
                        pass # Address might be directly in the info window without a specific label

                    # Extract phone
                    try:
                        phone_elem = info_window.find_element(By.XPATH, './/p[contains(text(), "Phone:")]')
                        phone = phone_elem.text.replace("Phone:", "").strip()
                    except:
                        pass

                    # Extract fax
                    try:
                        fax_elem = info_window.find_element(By.XPATH, './/p[contains(text(), "Fax:")]')
                        fax = fax_elem.text.replace("Fax:", "").strip()
                    except:
                        pass

                    # Extract website
                    try:
                        website_elem = info_window.find_element(By.XPATH, './/a[contains(@href, "http")]')
                        website = website_elem.get_attribute('href').strip()
                    except:
                        pass

                    parish_data = {
                        'name': parish_name,
                        'address': address,
                        'phone': phone,
                        'fax': fax,
                        'website': website,
                        'source_url': TARGET_URL,
                        'extraction_datetime': datetime.now().isoformat()
                    }
                    insert_parish_data(parish_data)
                    processed_parishes.add(parish_name)

                    # Close the info window to click on the next parish
                    try:
                        close_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.gm-ui-hover-effect')))
                        driver.execute_script("arguments[0].click();", close_button)
                        time.sleep(1) # Small delay after closing
                    except Exception as close_e:
                        print(f"Could not find or click close button: {close_e}")
                        # If close button not found, try to click outside or refresh to reset
                        driver.refresh()
                        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.corePrettyStyle > a > span')))


                except Exception as e:
                    print(f"Error processing parish {parish_name}: {e}")
                    # Try to close info window if it's open to proceed
                    try:
                        close_button = driver.find_element(By.CSS_SELECTOR, 'button.gm-ui-hover-effect')
                        driver.execute_script("arguments[0].click();", close_button)
                        time.sleep(1)
                    except:
                        pass
                    driver.refresh() # Refresh page to reset state if something went wrong
                    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.corePrettyStyle > a > span')))
                    continue # Continue to next parish

            # Check for "Next" button for pagination
            next_button = None
            try:
                # Look for a "Next" button or pagination link
                # This part is highly dependent on the website's pagination implementation
                # You might need to inspect the page to find the correct selector for the "Next" button
                # Example: next_button = driver.find_element(By.XPATH, '//a[text()="Next"]')
                # Or if it's a specific class/id:
                # next_button = driver.find_element(By.CSS_SELECTOR, 'a.next-page-link')
                # For this specific site, it seems to be a map, so pagination might be handled by map controls or not explicitly visible.
                # If there's no explicit pagination, it might be that all pins are loaded, or loaded on scroll/zoom.
                # Given the prompt, I'll assume there might be some hidden pagination or all are loaded.
                # If the number of parishes found is less than a certain threshold, or if the same parishes appear, it might indicate no more pages.

                # For this specific map, it seems all pins are loaded on the initial map load, and clicking on them reveals info.
                # The prompt mentioned "multiple pages", which might refer to a list view if one exists, or a misunderstanding of the map's behavior.
                # If all pins are indeed loaded, then the loop above will cover them.
                # If there's a "list view" that has pagination, we'd need to switch to that view first.
                # Based on the URL, it's a map view. I'll assume all pins are accessible from the initial load or by panning/zooming.
                # If there's no explicit "next page" button, we break the loop.
                print("No explicit 'Next' button found. Assuming all parishes are on the initial map or accessible via map interaction.")
                break # Exit loop if no next button is found or all parishes processed
            except Exception as e:
                print(f"No next button found or error finding it: {e}")
                break # Exit loop if no next button is found

        except Exception as e:
            print(f"Error during scraping loop: {e}\n{traceback.format_exc()}")
            break # Exit loop on general error

    driver.quit()
    print("Scraping complete.")

if __name__ == "__main__":
    scrape_parishes()
