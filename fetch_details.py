#!/usr/bin/env python3
"""
Fetch detailed information for each registration number in rx.json
and save to a new JSON file.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

# Configuration
INPUT_FILE = Path("rx.json")
OUTPUT_FILE = Path("pharmacists_detailed.json")
REQUEST_DELAY = 2  # seconds between requests to avoid overloading the server
BATCH_SIZE = 100  # Save progress after this many records

class DetailFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
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
            response = self.session.post(url, data=form_data, timeout=30)
            response.raise_for_status()
            
            # Parse the response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract the details table
            details = {}
            table = soup.find('table', {'class': 'table'})
            if not table:
                print(f"⚠️ No details found for {reg_number}")
                return None

            # Extract all rows from the table
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['th', 'td'])
                if len(cols) == 2:  # Key-value pair
                    key = cols[0].get_text(strip=True).lower().replace(' ', '_')
                    value = cols[1].get_text(strip=True)
                    details[key] = value
            
            # Add registration number to the details
            details['registration_number'] = reg_number
            
            return details
            
        except Exception as e:
            print(f"❌ Error fetching details for {reg_number}: {str(e)}")
            return None

def load_existing_data() -> List[Dict]:
    """Load existing data from the output file if it exists."""
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ Existing output file is corrupted. Starting fresh.")
    return []

def save_progress(data: List[Dict]) -> None:
    """Save the current progress to the output file."""
    temp_file = f"{OUTPUT_FILE}.tmp"
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Atomic write
    if os.path.exists(temp_file):
        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)
        os.rename(temp_file, OUTPUT_FILE)
    
    print(f"💾 Saved {len(data)} records to {OUTPUT_FILE}")

def main():
    # Load existing data to resume if interrupted
    existing_data = load_existing_data()
    processed_registrations = {item['registration_number'] for item in existing_data}
    
    # Load the registration numbers
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        registrations = json.load(f)
    
    print(f"📊 Found {len(registrations)} total registrations")
    print(f"📋 Already processed: {len(processed_registrations)}")
    
    fetcher = DetailFetcher()
    results = existing_data.copy()
    
    try:
        for i, record in enumerate(registrations, 1):
            reg_number = record['registration_number']
            
            # Skip already processed registrations
            if reg_number in processed_registrations:
                continue
            
            print(f"🔍 Processing {i}/{len(registrations)}: {reg_number}")
            
            # Fetch details
            details = fetcher.fetch_details(reg_number)
            
            if details:
                results.append(details)
                processed_registrations.add(reg_number)
                
                # Save progress periodically
                if len(results) % BATCH_SIZE == 0:
                    save_progress(results)
            
            # Be nice to the server
            time.sleep(REQUEST_DELAY)
            
    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
    finally:
        # Final save
        if results:
            save_progress(results)
        print("✅ Done!")

if __name__ == "__main__":
    main()
