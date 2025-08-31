
import sqlalchemy

DB_FILE = 'dioceses.db'
engine = sqlalchemy.create_engine(f'sqlite:///{DB_FILE}')
metadata = sqlalchemy.MetaData()

dioceses_table = sqlalchemy.Table('dioceses', metadata, autoload_with=engine)

with engine.connect() as connection:
    select_query = dioceses_table.select()
    result = connection.execute(select_query)

    for row in result:
        print(f"ID: {row.id}")
        print(f"  Name: {row.name}")
        print(f"  Website: {row.website}")
        print(f"  URL Status: {row.url_status}")
        print(f"  URL Checked At: {row.url_checked_at}")
        print(f"  Parish Listing Description: {row.parish_listing_description}")
        print(f"  Parish Listing URL: {row.parish_listing_url}")
        print(f"  Parish Listing Checked At: {row.parish_listing_checked_at}")
        print("--------------------------------------------------")

print("Analysis complete.")
