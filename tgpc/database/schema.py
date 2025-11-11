"""Database schema for pharmacist records."""
import sqlite3
from pathlib import Path
from typing import Optional


class PharmacistDB:
    """SQLite database for pharmacist records."""
    
    def __init__(self, db_path: str = "data/pharmacists.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None
    
    def connect(self):
        """Connect to the database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        """Create database tables."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pharmacists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                serial_number INTEGER UNIQUE NOT NULL,
                registration_number TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                father_name TEXT NOT NULL,
                category TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for fast searching
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_registration_number 
            ON pharmacists(registration_number)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_name 
            ON pharmacists(name)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category 
            ON pharmacists(category)
        """)
        
        self.conn.commit()
    
    def insert_pharmacist(self, serial_number: int, registration_number: str, 
                         name: str, father_name: str, category: str):
        """Insert a single pharmacist record."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO pharmacists 
            (serial_number, registration_number, name, father_name, category, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (serial_number, registration_number, name, father_name, category))
        self.conn.commit()
    
    def search(self, query: str, limit: int = 100):
        """Search pharmacists by name or registration number."""
        cursor = self.conn.cursor()
        search_pattern = f"%{query}%"
        
        cursor.execute("""
            SELECT serial_number, registration_number, name, father_name, category
            FROM pharmacists
            WHERE name LIKE ? OR registration_number LIKE ?
            ORDER BY serial_number DESC
            LIMIT ?
        """, (search_pattern, search_pattern, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_stats(self):
        """Get database statistics."""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total FROM pharmacists")
        total = cursor.fetchone()['total']
        
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM pharmacists 
            GROUP BY category
        """)
        by_category = {row['category']: row['count'] for row in cursor.fetchall()}
        
        return {
            'total_records': total,
            'by_category': by_category
        }
