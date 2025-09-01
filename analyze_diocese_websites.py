
import sqlalchemy
from datetime import datetime
import re

# Database setup
DB_FILE = 'dioceses.db'
engine = sqlalchemy.create_engine(f'sqlite:///{DB_FILE}')
metadata = sqlalchemy.MetaData()

# Reflect the existing table structure
dioceses_table = sqlalchemy.Table('dioceses', metadata, autoload_with=engine)
diocese_parish_lists_table = sqlalchemy.Table('diocese_parish_lists', metadata, autoload_with=engine)

def analyze_dioceses(max_dioceses_to_analyze=5):
    with engine.connect() as connection:
        with connection.begin(): # Explicit transaction for updates
            # Select dioceses that don't have a corresponding entry in diocese_parish_lists
            select_query = dioceses_table.select().where(
                ~dioceses_table.c.id.in_(
                    sqlalchemy.select(diocese_parish_lists_table.c.diocese_id)
                )
            ).limit(max_dioceses_to_analyze)
            
            result = connection.execute(select_query)

            for diocese in result:
                diocese_id = diocese.id
                website_url = diocese.website
                diocese_name = diocese.name

                print(f"Analyzing {diocese_name} ({website_url})")

                if website_url:
                    # Use web_fetch to analyze the website
                    prompt = f"Visit {website_url}. Identify all pages that list parishes or churches. For each listing, provide a short description and the direct URL. Examples: a clickable list of Parish Profiles, a static list of Parish Websites, an interactive map. If not available, state that. If the website is inaccessible, state that."
                    web_fetch_result = {"output": "Placeholder: No web_fetch call made yet."}

                    # Parse the web_fetch result
                    if "output" in web_fetch_result:
                        description_and_urls = web_fetch_result["output"]
                        # Find all URLs in the output
                        urls = re.findall(r'URL:\s*(https?://[\S]+)', description_and_urls)
                        descriptions = re.split(r'URL:\s*https?://[\S]+', description_and_urls)
                        descriptions = [d.strip() for d in descriptions if d.strip()]

                        if urls:
                            for i, url in enumerate(urls):
                                description = descriptions[i] if i < len(descriptions) else ""
                                insert_query = diocese_parish_lists_table.insert().values(
                                    diocese_id=diocese_id,
                                    parish_listing_description=description,
                                    parish_listing_url=url,
                                    parish_listing_checked_at=datetime.now()
                                )
                                connection.execute(insert_query)
                                print(f"Inserted parish list info for diocese ID {diocese_id}: {url}")
                        else:
                            # If no URLs are found, store the entire output as the description
                            insert_query = diocese_parish_lists_table.insert().values(
                                diocese_id=diocese_id,
                                parish_listing_description=description_and_urls.strip(),
                                parish_listing_url=None,
                                parish_listing_checked_at=datetime.now()
                            )
                            connection.execute(insert_query)
                            print(f"Inserted parish list info for diocese ID {diocese_id} (no URL found).")
                    else:
                        # Handle error fetching website
                        error_message = f"Error fetching website: {web_fetch_result.get('error', 'Unknown error')}"
                        insert_query = diocese_parish_lists_table.insert().values(
                            diocese_id=diocese_id,
                            parish_listing_description=error_message,
                            parish_listing_url=None,
                            parish_listing_checked_at=datetime.now()
                        )
                        connection.execute(insert_query)
                        print(f"Inserted parish list info for diocese ID {diocese_id} (fetch error).")

                else:
                    # Handle no website URL provided
                    insert_query = diocese_parish_lists_table.insert().values(
                        diocese_id=diocese_id,
                        parish_listing_description="No website URL provided.",
                        parish_listing_url=None,
                        parish_listing_checked_at=datetime.now()
                    )
                    connection.execute(insert_query)
                    print(f"Inserted parish list info for diocese ID {diocese_id} (no website URL).")

    print("Diocese website analysis complete.")

if __name__ == "__main__":
    analyze_dioceses()


