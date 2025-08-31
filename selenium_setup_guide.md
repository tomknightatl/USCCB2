# Selenium Setup Guide for Python Web Scraping

This guide outlines the steps to set up Selenium with Python for web scraping tasks that require browser automation.

## Prerequisites

*   **Python 3.x:** Ensure Python is installed on your system.
*   **Google Chrome Browser:** Selenium will control an instance of Chrome. Make sure it's installed and up to date.

## Step 1: Install the Selenium Python Library

It's highly recommended to install Python packages within a virtual environment to avoid conflicts with system-wide packages. If you're using a virtual environment (like the `venv` in this project), activate it first.

**To activate your virtual environment (if you have one):**

```bash
source venv/bin/activate
```

Once your virtual environment is activated (you should see `(venv)` at the beginning of your terminal prompt), run the following command to install the `selenium` package:

```bash
pip install selenium
```

## Step 2: Download the ChromeDriver

Selenium needs a browser-specific driver to interact with the browser. For Google Chrome, you need `ChromeDriver`.

1.  **Check your Chrome Browser Version:**
    *   Open Chrome.
    *   Go to `chrome://version` in the address bar.
    *   Note down your Chrome version number (e.g., `127.0.6533.110`).

2.  **Download ChromeDriver:**
    *   Go to the official ChromeDriver download page: [https://googlechromelabs.github.io/chrome-for-testing/](https://googlechromelabs.github.io/chrome-for-testing/)
    *   Find the ChromeDriver version that matches your Chrome browser version. Download the appropriate zip file for your operating system (e.g., `chromedriver-linux64.zip` for Linux).

3.  **Extract and Place ChromeDriver:**
    *   Extract the downloaded zip file. You will find an executable file named `chromedriver` (or `chromedriver.exe` on Windows).
    *   **Option A (Recommended - Add to PATH):** Move this `chromedriver` executable to a directory that is already in your system's PATH. Common locations include `/usr/local/bin` on Linux/macOS, or any directory you've added to your PATH environment variable. This allows Selenium to find the driver automatically.
    *   **Option B (Specify Path in Script):** If you prefer not to modify your PATH, you can place the `chromedriver` executable anywhere and then specify its full path in your Python script when initializing the Selenium WebDriver.

    *Example of specifying path in script:*
    ```python
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service

    # Replace with the actual path to your chromedriver executable
    webdriver_service = Service('/path/to/your/chromedriver')
    driver = webdriver.Chrome(service=webdriver_service)
    ```

## Step 3: Verify Installation

You can quickly test your setup with a simple Python script:

1.  Create a file named `test_selenium.py`:

    ```python
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    import time

    # If chromedriver is in your PATH, you can use:
    driver = webdriver.Chrome()

    # If you need to specify the path:
    # webdriver_service = Service('/path/to/your/chromedriver')
    # driver = webdriver.Chrome(service=webdriver_service)

    try:
        driver.get("https://www.google.com")
        print("Successfully opened Google!")
        time.sleep(3) # Wait for 3 seconds to see the browser
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit() # Close the browser
    ```

2.  Run the script from your terminal:

    ```bash
    python test_selenium.py
    ```

If a Chrome browser window opens and navigates to Google, your Selenium setup is successful!
