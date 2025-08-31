
import sqlalchemy
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

    if 'parish_listing_description' not in column_names:
        connection.execute(sqlalchemy.text("ALTER TABLE dioceses ADD COLUMN parish_listing_description TEXT"))
        print("Added parish_listing_description column.")
    if 'parish_listing_url' not in column_names:
        connection.execute(sqlalchemy.text("ALTER TABLE dioceses ADD COLUMN parish_listing_url TEXT"))
        print("Added parish_listing_url column.")
    if 'parish_listing_checked_at' not in column_names:
        connection.execute(sqlalchemy.text("ALTER TABLE dioceses ADD COLUMN parish_listing_checked_at DATETIME"))
        print("Added parish_listing_checked_at column.")

    # Re-reflect the table to include new columns
    dioceses_table = sqlalchemy.Table('dioceses', metadata, autoload_with=engine)

def analyze_dioceses():
    with engine.connect() as connection:
        with connection.begin(): # Explicit transaction for updates
            select_query = dioceses_table.select().where(dioceses_table.c.parish_listing_checked_at == None)
            
            

            result = connection.execute(select_query)

            for diocese in result:
                diocese_id = diocese.id
                website_url = diocese.website
                diocese_name = diocese.name

                parish_listing_description = ""
                parish_listing_url = ""
                parish_listing_checked_at = datetime.now()

                print(f"Analyzing {diocese_name} ({website_url})")

                if website_url:
                    # Use web_fetch to analyze the website
                    prompt = f"Visit {website_url}. How does this website list its parishes or churches? Provide a short description and the direct URL to the parish listing page if available. If not available, state that. If the website is inaccessible, state that."
                    web_fetch_result = {"output": "Placeholder: No web_fetch call made yet."}

                    # Parse the web_fetch result
                    if "output" in web_fetch_result:
                        description_and_url = web_fetch_result["output"]
                        # Attempt to parse the description and URL from the web_fetch output
                        # This parsing logic might need refinement based on actual web_fetch output format
                        if "URL:" in description_and_url:
                            parts = description_and_url.split("URL:", 1)
                            parish_listing_description = parts[0].strip()
                            parish_listing_url = parts[1].strip()
                        else:
                            parish_listing_description = description_and_url.strip()
                    else:
                        parish_listing_description = f"Error fetching website: {web_fetch_result.get('error', 'Unknown error')}"

                else:
                    parish_listing_description = "No website URL provided."

                # Update the database
                update_query = sqlalchemy.update(dioceses_table).where(dioceses_table.c.id == diocese_id).values(
                    parish_listing_description=parish_listing_description,
                    parish_listing_url=parish_listing_url,
                    parish_listing_checked_at=parish_listing_checked_at
                )
                connection.execute(update_query)
                print(f"Updated diocese ID {diocese_id}.")

    print("Diocese website analysis complete.")


