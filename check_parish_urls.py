import sqlite3
import requests
from datetime import datetime

DATABASE_PATH = '/home/tomk/USCCB2/dioceses.db'

def check_parish_url(url):
    """Checks if a given URL is valid (returns HTTP 200 OK)."""
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def update_diocese_url_status(diocese_id, is_valid, timestamp):
    """Updates the database with the URL validity and check timestamp."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE dioceses
            SET website_valid = ?,
                website_last_checked = ?
            WHERE id = ?
            """,
            (1 if is_valid else 0, timestamp, diocese_id)
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def main():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Add new columns if they don't exist
    try:
        cursor.execute("ALTER TABLE dioceses ADD COLUMN website_valid INTEGER")
        cursor.execute("ALTER TABLE dioceses ADD COLUMN website_last_checked TEXT")
        conn.commit()
        print("Added website_valid and website_last_checked columns to dioceses table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Columns website_valid and website_last_checked already exist.")
        else:
            raise e

    try:
        # Fetch all dioceses with a website URL
        cursor.execute("SELECT id, website FROM dioceses WHERE website IS NOT NULL")
        dioceses = cursor.fetchall()

        if not dioceses:
            print("No dioceses found with parish list URLs to check.")
            return

        print(f"Found {len(dioceses)} URLs to check.")

        for diocese_id, url in dioceses:
            print(f"Checking URL for Diocese ID {diocese_id}: {url}")
            is_valid = check_parish_url(url)
            timestamp = datetime.now().isoformat()
            update_diocese_url_status(diocese_id, is_valid, timestamp)
            status = "valid" if is_valid else "invalid"
            print(f"Updated Diocese ID {diocese_id}: URL is {status}.")

    except sqlite3.OperationalError as e:
        print(f"Error: {e}. Make sure the 'dioceses' table and columns 'parish_list_url', 'parish_list_url_valid', and 'parish_list_url_last_checked' exist in {DATABASE_PATH}.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
