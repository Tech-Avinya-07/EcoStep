import sqlite3

class Database:
    def __init__(self, db_path):
        # Add check_same_thread=False to allow multithreaded access
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.setup_table()

    def setup_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                carbon_footprint REAL NOT NULL,
                category TEXT NOT NULL,
                current_date TEXT NOT NULL  
            )
        ''')
        self.conn.commit()

    def insert_receipt_data(self, item_name, carbon_footprint, category,current_date):
        try:
            self.cursor.execute('''
                INSERT INTO receipts (item_name, carbon_footprint, category, current_date)
                VALUES (?, ?, ?, ?)
            ''', (item_name, carbon_footprint, category, current_date))
            
            self.conn.commit()
            return self.cursor.lastrowid  # Return the id of the inserted row
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()
            return None

    def close(self):
        self.conn.close()
