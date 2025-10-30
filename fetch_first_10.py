#!/usr/bin/env python3
"""
Fetch detailed information for the first 10 registration numbers in rx.json
and save to a new JSON file.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

# Configuration
INPUT_FILE = Path("rx.json")
OUTPUT_FILE = Path("first_10_pharmacists_detailed.json")
LIMIT = 10
REQUEST_DELAY = 2  # seconds between requests

class DetailFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })

    def fetch_details(self, reg_number: str) -> Optional[Dict]:
        """Fetch detailed information for a single registration number."""
        url = "https://www.pharmacycouncil.telangana.gov.in/pharmacy/getsearchpharmacist"
        
        form_data = {
            'registration_no': reg_number,
            'app_name': '',
            'father_name': '',
            'dob': '',
            'submit': 'Submit'
        }

        try:
            print(f"🔍 Fetching details for {reg_number}...")
            response = self.session.post(url, data=form_data, timeout=30)
            response.raise_for_status()
            
            # Parse the response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract the details table
            details = {'registration_number': reg_number}
            table = soup.find('table', {'class': 'table'})
            
            if not table:
                print(f"⚠️ No details table found for {reg_number}")
                return None

            # Extract all rows from the table
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['th', 'td'])
                if len(cols) == 2:  # Key-value pair
                    key = cols[0].get_text(strip=True).lower().replace(' ', '_')
                    value = cols[1].get_text(strip=True)
                    details[key] = value
            
            print(f"✅ Successfully fetched details for {reg_number}")
            return details
            
        except Exception as e:
            print(f"❌ Error fetching {reg_number}: {str(e)}")
            return None

def main():
    # Load the registration numbers
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        registrations = json.load(f)
    
    print(f"📊 Found {len(registrations)} total registrations")
    print(f"🔢 Will process first {min(LIMIT, len(registrations))} registrations")
    
    fetcher = DetailFetcher()
    results = []
    
    try:
        for i, record in enumerate(registrations[:LIMIT], 1):
            reg_number = record['registration_number']
            print(f"\n--- Processing {i}/{min(LIMIT, len(registrations))}: {reg_number} ---")
            
            # Fetch details
            details = fetcher.fetch_details(reg_number)
            
            if details:
                results.append(details)
                
                # Save after each successful fetch
                with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                print(f"💾 Saved {len(results)} records to {OUTPUT_FILE}")
            
            # Be nice to the server
            if i < LIMIT:  # No need to wait after the last request
                time.sleep(REQUEST_DELAY)
            
    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
    finally:
        print("\n✅ Done!")
        if results:
            print(f"📊 Fetched details for {len(results)}/{LIMIT} registrations")
            print(f"💾 Results saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
