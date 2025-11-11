"""Sync JSON data to SQLite database."""
import json
from pathlib import Path
from tgpc.database.schema import PharmacistDB


def sync_json_to_db(json_path: str = "data/rx.json", db_path: str = "data/pharmacists.db"):
    """Sync all records from JSON to database."""
    db = PharmacistDB(db_path)
    db.connect()
    db.create_tables()
    
    # Load JSON data
    with open(json_path, 'r', encoding='utf-8') as f:
        records = json.load(f)
    
    print(f"Syncing {len(records)} records to database...")
    
    # Insert all records
    for i, record in enumerate(records, 1):
        db.insert_pharmacist(
            serial_number=record['serial_number'],
            registration_number=record['registration_number'],
            name=record['name'],
            father_name=record['father_name'],
            category=record['category']
        )
        
        if i % 1000 == 0:
            print(f"  Synced {i}/{len(records)} records...")
    
    print(f"✅ Successfully synced {len(records)} records")
    
    # Show stats
    stats = db.get_stats()
    print(f"\n📊 Database Statistics:")
    print(f"  Total records: {stats['total_records']}")
    print(f"  By category:")
    for category, count in stats['by_category'].items():
        print(f"    {category}: {count}")
    
    db.close()
    return stats


if __name__ == "__main__":
    sync_json_to_db()
