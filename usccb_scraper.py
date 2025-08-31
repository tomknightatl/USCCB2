
import os
import requests
from bs4 import BeautifulSoup
import sqlalchemy

# Define the database schema
DB_FILE = 'dioceses.db'
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

engine = sqlalchemy.create_engine(f'sqlite:///{DB_FILE}')
metadata = sqlalchemy.MetaData()

dioceses_table = sqlalchemy.Table('dioceses', metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('name', sqlalchemy.String),
    sqlalchemy.Column('address', sqlalchemy.String),
    sqlalchemy.Column('website', sqlalchemy.String)
)

metadata.create_all(engine)

# Web scraping
URL = "https://www.usccb.org/about/bishops-and-dioceses/all-dioceses"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

with engine.begin() as connection:
    # Find all the diocese listings
    dioceses = soup.find_all("article", class_="node--type-da")
    print(f"Found {len(dioceses)} diocese listings.")

    for diocese in dioceses:
        name = diocese.find("span", class_="field--name-title").text.strip()
        print(f"Processing diocese: {name}")
        
        address_1_div = diocese.find("div", class_="field--name-field-da-address-1")
        address_2_div = diocese.find("div", class_="field--name-field-da-address-2")
        address = address_1_div.text.strip() if address_1_div else ""
        if address_2_div: address += ", " + address_2_div.text.strip()
        if not address_1_div and not address_2_div: print(f"  Address not found for {name}")

        website_div = diocese.find("div", class_="field--name-field-da-site")
        website = website_div.find("a")["href"] if website_div and website_div.find("a") else ""
        if not website_div: print(f"  Website not found for {name}")

        # Insert data into the database
        ins = dioceses_table.insert().values(
            name=name,
            address=address,
            website=website
        )
        connection.execute(ins)

print("Scraping and database population complete.")
