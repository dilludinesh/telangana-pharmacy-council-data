#!/usr/bin/env python3
"""
Quick script to verify data in Supabase.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    from supabase import create_client
except ImportError:
    print("❌ supabase library not installed. Run: pip install supabase")
    sys.exit(1)

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_KEY")

if not url or not key:
    print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env")
    sys.exit(1)

print("🔍 Checking Supabase data...")
print("=" * 60)

supabase = create_client(url, key)

# Get total count
response = supabase.table('rx').select('*', count='exact').limit(1).execute()
total = response.count if hasattr(response, 'count') else 0

print(f"✅ Total records in Supabase: {total:,}")

# Get a sample record
sample = supabase.table('rx').select('*').limit(1).execute()
if sample.data:
    record = sample.data[0]
    print(f"\n📋 Sample record:")
    print(f"   Registration: {record.get('registration_number')}")
    print(f"   Name: {record.get('name')}")
    print(f"   Category: {record.get('category')}")

# Get category breakdown
categories = supabase.table('rx').select('category').execute()
if categories.data:
    from collections import Counter
    cat_counts = Counter(r['category'] for r in categories.data)
    print(f"\n📊 By category:")
    for cat, count in sorted(cat_counts.items()):
        print(f"   {cat}: {count:,}")

print("\n" + "=" * 60)
print("✅ Supabase verification complete!")
