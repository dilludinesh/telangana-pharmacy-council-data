#!/usr/bin/env python3
"""
Sync pharmacist records from rx.json to Supabase database.
This script is run by GitHub Actions after updating rx.json.
"""

import json
import os
import sys

from supabase import Client, create_client


def load_records(file_path: str) -> list:
    """Load pharmacist records from rx.json file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            records = json.load(f)
        print(f"✓ Loaded {len(records)} records from {file_path}")
        return records
    except FileNotFoundError:
        print(f"✗ Error: File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"✗ Error: Invalid JSON in {file_path}: {e}")
        sys.exit(1)


def init_supabase() -> Client:
    """Initialize Supabase client with credentials from environment variables."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")

    if not url or not key:
        print("✗ Error: Missing Supabase credentials")
        print("  Required environment variables:")
        print("  - SUPABASE_URL")
        print("  - SUPABASE_SERVICE_KEY")
        sys.exit(1)

    try:
        supabase = create_client(url, key)
        print("✓ Connected to Supabase")
        return supabase
    except Exception as e:
        print(f"✗ Error connecting to Supabase: {e}")
        sys.exit(1)


def sync_records(supabase: Client, records: list) -> dict:
    """
    Sync records to Supabase using upsert (insert or update).
    Returns statistics about the sync operation.
    """
    stats = {
        "total": len(records),
        "synced": 0,
        "errors": 0,
        "error_details": []
    }

    print(f"\nSyncing {stats['total']} records to Supabase...")

    # Batch upsert for better performance
    batch_size = 1000
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]

        try:
            # Upsert batch (insert new or update existing based on registration_number)
            supabase.table('rx').upsert(
                batch,
                on_conflict='registration_number'
            ).execute()

            stats['synced'] += len(batch)
            print(f"  ✓ Synced batch {i//batch_size + 1}: {len(batch)} records")

        except Exception as e:
            stats['errors'] += len(batch)
            error_msg = f"Batch {i//batch_size + 1} failed: {str(e)}"
            stats['error_details'].append(error_msg)
            print(f"  ✗ {error_msg}")

    return stats


def main():
    """Main function to orchestrate the sync process."""
    print("=" * 60)
    print("TGPC Pharmacist Data Sync to Supabase")
    print("=" * 60)

    # Load records from rx.json
    records = load_records('data/rx.json')

    # Initialize Supabase client
    supabase = init_supabase()

    # Sync records
    stats = sync_records(supabase, records)

    # Print summary
    print("\n" + "=" * 60)
    print("Sync Summary")
    print("=" * 60)
    print(f"Total records:   {stats['total']}")
    print(f"Synced:          {stats['synced']}")
    print(f"Errors:          {stats['errors']}")

    if stats['error_details']:
        print("\nError Details:")
        for error in stats['error_details']:
            print(f"  - {error}")

    # Exit with error code if there were errors
    if stats['errors'] > 0:
        print("\n✗ Sync completed with errors")
        sys.exit(1)
    else:
        print("\n✓ Sync completed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
