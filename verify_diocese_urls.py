
import sqlalchemy
import requests
from datetime import datetime

# Database setup
DB_FILE = 'dioceses.db'
engine = sqlalchemy.create_engine(f'sqlite:///{DB_FILE}')
metadata = sqlalchemy.MetaData()

# Reflect the existing table structure
dioceses_table = sqlalchemy.Table('dioceses', metadata, autoload_with=engine)

# Add new columns if they don't exist
with engine.connect() as connection:
    inspector = sqlalchemy.inspect(engine)
    columns = inspector.get_columns('dioceses')
    column_names = [col['name'] for col in columns]

    if 'url_status' not in column_names:
        connection.execute(sqlalchemy.text("ALTER TABLE dioceses ADD COLUMN url_status TEXT"))
        print("Added url_status column.")
    if 'url_checked_at' not in column_names:
        connection.execute(sqlalchemy.text("ALTER TABLE dioceses ADD COLUMN url_checked_at DATETIME"))
        print("Added url_checked_at column.")

# Re-reflect the table to include new columns
dioceses_table = sqlalchemy.Table('dioceses', metadata, autoload_with=engine)

# Iterate through dioceses and verify URLs
with engine.connect() as connection:
    select_query = dioceses_table.select()
    result = connection.execute(select_query)

    for diocese in result:
        diocese_id = diocese.id
        website_url = diocese.website
        
        url_status = ""
        url_checked_at = datetime.now()

        if website_url:
            try:
                response = requests.head(website_url, allow_redirects=True, timeout=5)
                url_status = str(response.status_code)
            except requests.exceptions.RequestException as e:
                url_status = f"Error: {e}"
        else:
            url_status = "No URL provided"

        # Update the database
        update_query = sqlalchemy.update(dioceses_table).where(dioceses_table.c.id == diocese_id).values(
            url_status=url_status,
            url_checked_at=url_checked_at
        )
        connection.execute(update_query)
        print(f"Updated diocese ID {diocese_id}: URL Status - {url_status}")

print("URL verification complete.")
