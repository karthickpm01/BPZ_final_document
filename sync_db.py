import sqlite3
import os

# Configuration
DB_FILE = 'database.db'
PDF_FOLDER = 'static/pdfs'


def sync_existing_files():
    # 1. Check if folder exists
    if not os.path.exists(PDF_FOLDER):
        print(f"Error: Folder '{PDF_FOLDER}' not found.")
        return

    # 2. Connect to Database
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # 3. Get list of files from Hard Drive
    physical_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith('.pdf')]

    print(f"Found {len(physical_files)} PDFs in folder...")

    count = 0
    for filename in physical_files:
        filepath = os.path.join(PDF_FOLDER, filename)

        # Check if file is already in DB
        exists = c.execute("SELECT * FROM files WHERE filename = ?", (filename,)).fetchone()

        if not exists:
            c.execute("INSERT INTO files (filename, filepath) VALUES (?, ?)", (filename, filepath))
            print(f"Added to DB: {filename}")
            count += 1
        else:
            print(f"Already in DB: {filename}")

    conn.commit()
    conn.close()
    print(f"--- Sync Complete. Added {count} new files to the Dashboard. ---")


if __name__ == "__main__":
    sync_existing_files()