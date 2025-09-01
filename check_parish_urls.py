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

def update_parish_list_url_status(parish_list_id, is_valid, timestamp):
    """Updates the database with the URL validity and check timestamp."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE diocese_parish_lists
            SET website_valid = ?,
                website_last_checked = ?
            WHERE id = ?
            """,
            (1 if is_valid else 0, timestamp, parish_list_id)
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def main():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Fetch all parish lists with a website URL
        cursor.execute("SELECT id, parish_listing_url FROM diocese_parish_lists WHERE parish_listing_url IS NOT NULL")
        parish_lists = cursor.fetchall()

        if not parish_lists:
            print("No parish list URLs to check.")
            return

        print(f"Found {len(parish_lists)} URLs to check.")

        for parish_list_id, url in parish_lists:
            print(f"Checking URL for Parish List ID {parish_list_id}: {url}")
            is_valid = check_parish_url(url)
            timestamp = datetime.now().isoformat()
            update_parish_list_url_status(parish_list_id, is_valid, timestamp)
            status = "valid" if is_valid else "invalid"
            print(f"Updated Parish List ID {parish_list_id}: URL is {status}.")

    except sqlite3.OperationalError as e:
        print(f"Error: {e}. Make sure the 'diocese_parish_lists' table and columns exist in {DATABASE_PATH}.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
