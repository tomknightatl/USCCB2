
import sqlalchemy

DB_FILE = 'dioceses.db'
engine = sqlalchemy.create_engine(f'sqlite:///{DB_FILE}')
metadata = sqlalchemy.MetaData()

dioceses_table = sqlalchemy.Table('dioceses', metadata, autoload_with=engine)
diocese_parish_lists_table = sqlalchemy.Table('diocese_parish_lists', metadata, autoload_with=engine)

with engine.connect() as connection:
    select_query = sqlalchemy.select(dioceses_table, diocese_parish_lists_table).join(diocese_parish_lists_table, dioceses_table.c.id == diocese_parish_lists_table.c.diocese_id)
    result = connection.execute(select_query)

    for row in result:
        print(f"Diocese ID: {row.id}")
        print(f"  Name: {row.name}")
        print(f"  Website: {row.website}")
        print(f"  URL Status: {row.url_status}")
        print(f"  URL Checked At: {row.url_checked_at}")
        print(f"  Parish Listing ID: {row.id_1}")
        print(f"  Parish Listing Description: {row.parish_listing_description}")
        print(f"  Parish Listing URL: {row.parish_listing_url}")
        print(f"  Parish Listing Checked At: {row.parish_listing_checked_at}")
        print(f"  Website Valid: {row.website_valid}")
        print(f"  Website Last Checked: {row.website_last_checked}")
        print(f"  Listing Type: {row.listing_type}")
        print(f"  Listing Type Checked At: {row.listing_type_checked_at}")
        print("--------------------------------------------------")

print("Analysis complete.")
