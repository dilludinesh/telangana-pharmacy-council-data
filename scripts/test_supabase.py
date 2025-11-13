#!/usr/bin/env python3
"""
Quick test script to verify Supabase connection and table setup.
Run this after setting up your .env file with Supabase credentials.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from supabase import create_client
except ImportError:
    print("❌ Error: supabase library not installed")
    print("Run: pip install supabase")
    sys.exit(1)


def test_connection():
    """Test basic connection to Supabase."""
    print("🔍 Testing Supabase Connection...")
    print("=" * 60)
    
    # Get credentials
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    
    if not url or not key:
        print("❌ Missing credentials in .env file")
        print("\nRequired variables:")
        print("  - SUPABASE_URL")
        print("  - SUPABASE_SERVICE_KEY")
        print("\nCreate a .env file with these values from your Supabase dashboard.")
        return False
    
    print(f"✓ Found SUPABASE_URL: {url[:30]}...")
    print(f"✓ Found SUPABASE_SERVICE_KEY: {key[:20]}...")
    
    # Try to connect
    try:
        supabase = create_client(url, key)
        print("✓ Connected to Supabase successfully!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    # Test table access
    try:
        response = supabase.table('rx').select('count', count='exact').execute()
        count = response.count if hasattr(response, 'count') else 0
        print(f"✓ Table 'rx' exists with {count} records")
    except Exception as e:
        print(f"❌ Table access failed: {e}")
        print("\nMake sure you've run the SQL schema in Supabase SQL Editor:")
        print("  File: scripts/supabase_setup.sql")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! Your Supabase is ready.")
    print("\nNext steps:")
    print("  1. Add secrets to GitHub (SUPABASE_URL, SUPABASE_SERVICE_KEY)")
    print("  2. Run: python scripts/sync_to_supabase.py")
    print("  3. Check your Supabase dashboard to see the data")
    return True


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
