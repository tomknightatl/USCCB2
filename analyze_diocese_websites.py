
import sqlalchemy
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Database setup
DB_FILE = 'dioceses.db'
engine = sqlalchemy.create_engine(f'sqlite:///{DB_FILE}')
metadata = sqlalchemy.MetaData()

# Reflect the existing table structure
dioceses_table = sqlalchemy.Table('dioceses', metadata, autoload_with=engine)
diocese_parish_lists_table = sqlalchemy.Table('diocese_parish_lists', metadata, autoload_with=engine)

def is_parish_listing_page(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Check title and common elements for keywords
        text_content = soup.get_text().lower()
        keywords = ['parish', 'church', 'directory', 'list', 'map', 'find', 'locations']
        if any(keyword in text_content for keyword in keywords):
            # Look for multiple links that might represent individual parishes
            parish_link_count = 0
            for link in soup.find_all('a', href=True):
                link_text = link.get_text().lower()
                link_href = link['href']
                if any(keyword in link_text or keyword in link_href for keyword in keywords):
                    parish_link_count += 1
                if parish_link_count > 5: # Arbitrary threshold for multiple parish links
                    return True
        return False
    except requests.exceptions.RequestException:
        return False

def analyze_dioceses(max_dioceses_to_analyze=5):
    with engine.connect() as connection:
        with connection.begin(): # Explicit transaction for updates
            # Select dioceses that don't have a corresponding entry in diocese_parish_lists
            # or select the oldest entries if all dioceses have been analyzed
            select_query_missing = dioceses_table.select().where(
                ~dioceses_table.c.id.in_(
                    sqlalchemy.select(diocese_parish_lists_table.c.diocese_id)
                )
            ).limit(max_dioceses_to_analyze)
            
            result_missing = connection.execute(select_query_missing).fetchall()

            dioceses_to_analyze = []

            if len(result_missing) < max_dioceses_to_analyze:
                # If there are not enough missing dioceses, get the oldest analyzed ones
                select_query_oldest = sqlalchemy.select(dioceses_table).join(diocese_parish_lists_table, dioceses_table.c.id == diocese_parish_lists_table.c.diocese_id).where(
                    dioceses_table.c.id.in_(
                        sqlalchemy.select(diocese_parish_lists_table.c.diocese_id)
                    )
                ).order_by(diocese_parish_lists_table.c.parish_listing_checked_at.asc()).limit(max_dioceses_to_analyze - len(result_missing))
                
                result_oldest = connection.execute(select_query_oldest).fetchall()
                dioceses_to_analyze = list(result_missing) + list(result_oldest)
            else:
                dioceses_to_analyze = list(result_missing)

            for diocese in dioceses_to_analyze:
                diocese_id = diocese.id
                website_url = diocese.website
                diocese_name = diocese.name

                # If the diocese is already in diocese_parish_lists, we need to get its current data
                if diocese.id in [d.id for d in result_oldest]:
                    # Fetch the full diocese object again to ensure all columns are present
                    diocese = connection.execute(dioceses_table.select().where(dioceses_table.c.id == diocese.id)).fetchone()

                print(f"Analyzing {diocese_name} ({website_url})")

                # Delete existing entries for this diocese if re-analyzing
                delete_query = diocese_parish_lists_table.delete().where(diocese_parish_lists_table.c.diocese_id == diocese.id)
                connection.execute(delete_query)

                if diocese.website:
                    try:
                        response = requests.get(website_url, timeout=10, import sqlalchemy
from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Database setup
DB_FILE = 'dioceses.db'
engine = sqlalchemy.create_engine(f'sqlite:///{DB_FILE}')
metadata = sqlalchemy.MetaData()

# Reflect the existing table structure
dioceses_table = sqlalchemy.Table('dioceses', metadata, autoload_with=engine)
diocese_parish_lists_table = sqlalchemy.Table('diocese_parish_lists', metadata, autoload_with=engine)

def is_parish_listing_page(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Check title and common elements for keywords
        text_content = soup.get_text().lower()
        keywords = ['parish', 'church', 'directory', 'list', 'map', 'find', 'locations']
        if any(keyword in text_content for keyword in keywords):
            # Look for multiple links that might represent individual parishes
            parish_link_count = 0
            for link in soup.find_all('a', href=True):
                link_text = link.get_text().lower()
                link_href = link['href']
                if any(keyword in link_text or keyword in link_href for keyword in keywords):
                    parish_link_count += 1
                if parish_link_count > 5: # Arbitrary threshold for multiple parish links
                    return True
        return False
    except requests.exceptions.RequestException:
        return False

def analyze_dioceses(max_dioceses_to_analyze=5):
    # Setup Selenium WebDriver options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # Path to chromedriver, assuming it's in /usr/bin/ or accessible via PATH
    service = Service('/usr/bin/chromedriver')

    with webdriver.Chrome(service=service, options=chrome_options) as driver:
        with engine.connect() as connection:
            with connection.begin(): # Explicit transaction for updates
                # Select dioceses that don't have a corresponding entry in diocese_parish_lists
                # or select the oldest entries if all dioceses have been analyzed
                select_query_missing = dioceses_table.select().where(
                    ~dioceses_table.c.id.in_(
                        sqlalchemy.select(diocese_parish_lists_table.c.diocese_id)
                    )
                ).limit(max_dioceses_to_analyze)
                
                result_missing = connection.execute(select_query_missing).fetchall()

                dioceses_to_analyze = []

                if len(result_missing) < max_dioceses_to_analyze:
                    # If there are not enough missing dioceses, get the oldest analyzed ones
                    select_query_oldest = sqlalchemy.select(dioceses_table).join(diocese_parish_lists_table, dioceses_table.c.id == diocese_parish_lists_table.c.diocese_id).where(
                        dioceses_table.c.id.in_(
                            sqlalchemy.select(diocese_parish_lists_table.c.diocese_id)
                        )
                    ).order_by(diocese_parish_lists_table.c.parish_listing_checked_at.asc()).limit(max_dioceses_to_analyze - len(result_missing))
                    
                    result_oldest = connection.execute(select_query_oldest).fetchall()
                    dioceses_to_analyze = list(result_missing) + list(result_oldest)
                else:
                    dioceses_to_analyze = list(result_missing)

                for diocese in dioceses_to_analyze:
                    diocese_id = diocese.id
                    website_url = diocese.website
                    diocese_name = diocese.name

                    # If the diocese is already in diocese_parish_lists, we need to get its current data
                    if diocese.id in [d.id for d in result_oldest]:
                        # Fetch the full diocese object again to ensure all columns are present
                        diocese = connection.execute(dioceses_table.select().where(dioceses_table.c.id == diocese.id)).fetchone()

                    print(f"Analyzing {diocese_name} ({website_url})")

                    # Delete existing entries for this diocese if re-analyzing
                    delete_query = diocese_parish_lists_table.delete().where(diocese_parish_lists_table.c.diocese_id == diocese.id)
                    connection.execute(delete_query)

                    if diocese.website:
                        page_content = None
                        try:
                            # First, try with requests
                            response = requests.get(website_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'})
                            response.raise_for_status()
                            page_content = response.content
                        except requests.exceptions.RequestException as e:
                            if e.response is not None and e.response.status_code == 403:
                                print(f"Requests failed for {website_url} with 403. Trying Selenium...")
                                try:
                                    driver.get(website_url)
                                    page_content = driver.page_source
                                except Exception as selenium_e:
                                    error_message = f"Selenium also failed for {website_url}: {selenium_e}"
                                    insert_query = diocese_parish_lists_table.insert().values(
                                        diocese_id=diocese_id,
                                        parish_listing_description=error_message,
                                        parish_listing_url=None,
                                        parish_listing_checked_at=datetime.now()
                                    )
                                    connection.execute(insert_query)
                                    print(f"Inserted for Diocese ID {diocese_id}: Description='{error_message}', URL=None")
                                    continue # Skip to the next diocese
                            else:
                                error_message = f"Error fetching website: {e}"
                                insert_query = diocese_parish_lists_table.insert().values(
                                    diocese_id=diocese_id,
                                    parish_listing_description=error_message,
                                    parish_listing_url=None,
                                    parish_listing_checked_at=datetime.now()
                                )
                                connection.execute(insert_query)
                                print(f"Inserted for Diocese ID {diocese_id}: Description='{error_message}', URL=None")
                                continue # Skip to the next diocese

                        if page_content:
                            soup = BeautifulSoup(page_content, 'html.parser')

                            found_listings = []
                            processed_urls = set()

                            # Look for common links related to parish listings
                            keywords = ['parish', 'church', 'directory', 'find', 'map', 'locations']
                            for link in soup.find_all('a', href=True):
                                link_text = link.get_text().lower()
                                link_href = link['href']

                                if link_href.startswith('javascript'):
                                    continue # Skip javascript links

                                absolute_url = urljoin(website_url, link_href)

                                if (diocese_id, absolute_url) in processed_urls:
                                    continue # Skip if already processed for this diocese

                                if any(keyword in link_text or keyword in absolute_url for keyword in keywords):
                                    if is_parish_listing_page(absolute_url):
                                        found_listings.append({
                                            'description': link_text.strip() or f"Link to {absolute_url}",
                                            'url': absolute_url
                                        })
                                        processed_urls.add((diocese_id, absolute_url))
                            
                            if found_listings:
                                for listing in found_listings:
                                    insert_query = diocese_parish_lists_table.insert().values(
                                        diocese_id=diocese_id,
                                        parish_listing_description=listing['description'],
                                        parish_listing_url=listing['url'],
                                        parish_listing_checked_at=datetime.now()
                                    )
                                    connection.execute(insert_query)
                                    print(f"Inserted for Diocese ID {diocese_id}: Description='{listing['description']}', URL='{listing['url']}'")
                            else:
                                # If no specific links are found, store the main website URL with a generic description
                                insert_query = diocese_parish_lists_table.insert().values(
                                    diocese_id=diocese_id,
                                    parish_listing_description="No specific parish listing links found. Main website analyzed.",
                                    parish_listing_url=website_url,
                                    parish_listing_checked_at=datetime.now()
                                )
                                connection.execute(insert_query)
                                print(f"Inserted for Diocese ID {diocese_id}: Description='No specific parish listing links found. Main website analyzed.', URL='{website_url}'")

                        else:
                            # Handle no website URL provided
                            insert_query = diocese_parish_lists_table.insert().values(
                                diocese_id=diocese_id,
                                parish_listing_description="No website URL provided.",
                                parish_listing_url=None,
                                parish_listing_checked_at=datetime.now()
                            )
                            connection.execute(insert_query)
                            print(f"Inserted for Diocese ID {diocese_id}: Description='No website URL provided.', URL=None")

        print("Diocese website analysis complete.")

if __name__ == "__main__":
    analyze_dioceses()
)
                        response.raise_for_status() # Raise an exception for HTTP errors
                        soup = BeautifulSoup(response.content, 'html.parser')

                        found_listings = []
                        processed_urls = set()

                        # Look for common links related to parish listings
                        keywords = ['parish', 'church', 'directory', 'find', 'map', 'locations']
                        for link in soup.find_all('a', href=True):
                            link_text = link.get_text().lower()
                            link_href = link['href']

                            if link_href.startswith('javascript'):
                                continue # Skip javascript links

                            absolute_url = urljoin(website_url, link_href)

                            if (diocese_id, absolute_url) in processed_urls:
                                continue # Skip if already processed for this diocese

                            if any(keyword in link_text or keyword in absolute_url for keyword in keywords):
                                if is_parish_listing_page(absolute_url):
                                    found_listings.append({
                                        'description': link_text.strip() or f"Link to {absolute_url}",
                                        'url': absolute_url
                                    })
                                    processed_urls.add((diocese_id, absolute_url))
                        
                        if found_listings:
                            for listing in found_listings:
                                insert_query = diocese_parish_lists_table.insert().values(
                                    diocese_id=diocese_id,
                                    parish_listing_description=listing['description'],
                                    parish_listing_url=listing['url'],
                                    parish_listing_checked_at=datetime.now()
                                )
                                connection.execute(insert_query)
                                print(f"Inserted for Diocese ID {diocese_id}: Description='{listing['description']}', URL='{listing['url']}'")
                        else:
                            # If no specific links are found, store the main website URL with a generic description
                            insert_query = diocese_parish_lists_table.insert().values(
                                diocese_id=diocese_id,
                                parish_listing_description="No specific parish listing links found. Main website analyzed.",
                                parish_listing_url=website_url,
                                parish_listing_checked_at=datetime.now()
                            )
                            connection.execute(insert_query)
                            print(f"Inserted for Diocese ID {diocese_id}: Description='No specific parish listing links found. Main website analyzed.', URL='{website_url}'")

                    except requests.exceptions.RequestException as e:
                        if e.response is not None and e.response.status_code == 403:
                            print(f"Skipping Diocese ID {diocese_id} due to 403 Forbidden error for {website_url}")
                            continue # Skip to the next diocese
                        else:
                            error_message = f"Error fetching website: {e}"
                            insert_query = diocese_parish_lists_table.insert().values(
                                diocese_id=diocese_id,
                                parish_listing_description=error_message,
                                parish_listing_url=None,
                                parish_listing_checked_at=datetime.now()
                            )
                            connection.execute(insert_query)
                            print(f"Inserted for Diocese ID {diocese_id}: Description='{error_message}', URL=None")

                else:
                    # Handle no website URL provided
                    insert_query = diocese_parish_lists_table.insert().values(
                        diocese_id=diocese_id,
                        parish_listing_description="No website URL provided.",
                        parish_listing_url=None,
                        parish_listing_checked_at=datetime.now()
                    )
                    connection.execute(insert_query)
                    print(f"Inserted for Diocese ID {diocese_id}: Description='No website URL provided.', URL=None")

    print("Diocese website analysis complete.")

if __name__ == "__main__":
    analyze_dioceses()


