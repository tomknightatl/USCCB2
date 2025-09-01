
import sqlalchemy
from datetime import datetime

# Database setup
DB_FILE = 'dioceses.db'
engine = sqlalchemy.create_engine(f'sqlite:///{DB_FILE}')
metadata = sqlalchemy.MetaData()

# Reflect the existing table structure
dioceses_table = sqlalchemy.Table('dioceses', metadata, autoload_with=engine)
diocese_parish_lists_table = sqlalchemy.Table('diocese_parish_lists', metadata, autoload_with=engine)

def classify_listing_types(max_dioceses_to_visit=None):
    with engine.connect() as connection:
        with connection.begin(): # Explicit transaction for updates
            select_query = sqlalchemy.select(
                dioceses_table.c.id.label('diocese_id'),
                dioceses_table.c.name.label('diocese_name'),
                diocese_parish_lists_table.c.id.label('parish_list_id'),
                diocese_parish_lists_table.c.parish_listing_url
            ).join(diocese_parish_lists_table, dioceses_table.c.id == diocese_parish_lists_table.c.diocese_id).where(
                sqlalchemy.and_(
                    diocese_parish_lists_table.c.parish_listing_url != None,
                    diocese_parish_lists_table.c.listing_type_checked_at == None
                )
            )
            
            if max_dioceses_to_visit:
                select_query = select_query.limit(max_dioceses_to_visit)

            result = connection.execute(select_query)

            for row in result:
                diocese_id = row.diocese_id
                parish_list_id = row.parish_list_id
                parish_listing_url = row.parish_listing_url
                diocese_name = row.diocese_name

                listing_type = ""
                listing_type_checked_at = datetime.now()

                print(f"Classifying listing type for {diocese_name} ({parish_listing_url})")

                if parish_listing_url:
                    prompt = f"Visit {parish_listing_url}. Describe how parishes are listed on this page. Is it an interactive map, a simple list, a search form, a PDF document, or something else? Be concise."
                    print(f"WEB_FETCH_PROMPT: {prompt}")
                    return # Exit after printing the prompt for the first diocese

                else:
                    listing_type = "No parish listing URL provided."

                # Update the database
                update_query = sqlalchemy.update(diocese_parish_lists_table).where(diocese_parish_lists_table.c.id == parish_list_id).values(
                    listing_type=listing_type,
                    listing_type_checked_at=listing_type_checked_at
                )
                connection.execute(update_query)
                print(f"Updated diocese ID {diocese_id} with listing type: {listing_type}")

    print("Listing type classification complete.")

if __name__ == "__main__":
    # Example usage: classify 5 dioceses for testing
    classify_listing_types(max_dioceses_to_visit=5)
    # To classify all unvisited dioceses, call without a parameter:
    # classify_listing_types()
