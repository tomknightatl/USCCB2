
import sqlalchemy
from datetime import datetime
import sys

if len(sys.argv) != 4:
    print("Usage: python update_db_entry.py <diocese_id> <description> <url>")
    sys.exit(1)

diocese_id = int(sys.argv[1])
description = sys.argv[2]
url = sys.argv[3]

DB_FILE = 'dioceses.db'
engine = sqlalchemy.create_engine(f'sqlite:///{DB_FILE}')
metadata = sqlalchemy.MetaData()

dioceses_table = sqlalchemy.Table('dioceses', metadata, autoload_with=engine)

with engine.connect() as connection:
    with connection.begin():
        update_query = sqlalchemy.update(dioceses_table).where(dioceses_table.c.id == diocese_id).values(
            parish_listing_description=description,
            parish_listing_url=url,
            parish_listing_checked_at=datetime.now()
        )
        connection.execute(update_query)

print(f"Updated diocese ID {diocese_id}.")
