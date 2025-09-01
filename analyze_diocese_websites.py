
import sqlalchemy
from datetime import datetime

# Database setup
DB_FILE = 'dioceses.db'
engine = sqlalchemy.create_engine(f'sqlite:///{DB_FILE}')
metadata = sqlalchemy.MetaData()

# Reflect the existing table structure
dioceses_table = sqlalchemy.Table('dioceses', metadata, autoload_with=engine)
2diocese_parish_lists_table = sqlalchemy.Table('diocese_parish_lists', metadata, autoload_with=engine)

def analyze_dioceses():
    with engine.connect() as connection:
        with connection.begin(): # Explicit transaction for updates
            # Select dioceses that don't have a corresponding entry in diocese_parish_lists
            select_query = dioceses_table.select().where(
                ~dioceses_table.c.id.in_(
                    sqlalchemy.select(diocese_parish_lists_table.c.diocese_id)
                )
            )
            
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

                # Insert into the new table
                insert_query = diocese_parish_lists_table.insert().values(
                    diocese_id=diocese_id,
                    parish_listing_description=parish_listing_description,
                    parish_listing_url=parish_listing_url,
                    parish_listing_checked_at=parish_listing_checked_at
                )
                connection.execute(insert_query)
                print(f"Inserted parish list info for diocese ID {diocese_id}.")

    print("Diocese website analysis complete.")


