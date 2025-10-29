import argparse
import requests
import time
import random
import json
import re
import sys
from bs4 import BeautifulSoup
import os
from datetime import datetime

class Reader:
    def __init__(self, dataset_path="rx.json"):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

        self.dataset_path = dataset_path
        self.progress_file = 'scraping_progress.json'
        self.enhanced_data_file = 'pharmacists_detailed.json'

        # Rate limiting settings
        self.min_delay = 2  # Minimum seconds between requests
        self.max_delay = 5  # Maximum seconds between requests
        self.long_break_after = 100  # Take longer break after every 100 requests
        self.long_break_duration = 30  # 30 seconds break

    def load_progress(self):
        """Load progress from file"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {'completed': [], 'failed': [], 'last_index': 0}

    def save_progress(self, completed, failed, last_index):
        """Save progress to file"""
        progress = {
            'completed': completed,
            'failed': failed,
            'last_index': last_index,
            'timestamp': datetime.now().isoformat()
        }
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)

    def load_existing_data(self):
        """Load existing basic pharmacist data"""
        if os.path.exists(self.dataset_path):
            with open(self.dataset_path, 'r') as f:
                return json.load(f)
        return []

    def make_request(self, url, data=None):
        """Make a request with error handling"""
        try:
            if data:
                response = self.session.post(url, data=data, timeout=30)
            else:
                response = self.session.get(url, timeout=30)

            # Check for blocking indicators
            if response.status_code == 403:
                print("🚫 403 Forbidden - Possible blocking detected!")
                return None
            elif response.status_code == 429:
                print("🐌 429 Rate Limited - Need to slow down!")
                return None
            elif response.status_code != 200:
                print(f"❌ HTTP {response.status_code} - Error")
                return None

            # Add random delay between requests
            delay = random.uniform(self.min_delay, self.max_delay)
            print(f"⏱️  Waiting {delay:.1f}s...")
            time.sleep(delay)

            return response

        except requests.exceptions.RequestException as e:
            print(f"🔥 Request error: {e}")
            return None

    def get_total_pharmacist_count(self):
        """Fetch the total count of pharmacists listed on the council website"""
        total_url = "https://www.pharmacycouncil.telangana.gov.in/pharmacy/srchpharmacisttotal"
        print("🌐 Fetching total pharmacist listing page...")
        response = self.make_request(total_url)
        if not response:
            print("⚠️  Unable to retrieve the total pharmacists page.")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        table = soup.find('table', attrs={'id': 'tablesorter-demo'})
        if not table:
            tables = soup.find_all('table')
            table = tables[0] if tables else None

        if not table:
            print("❓ Could not locate the pharmacists table on the page.")
            return None

        data_rows = [row for row in table.find_all('tr') if row.find_all('td')]
        if not data_rows:
            print("❓ No pharmacist rows found in the table.")
            return None

        serial_numbers = []
        for row in data_rows:
            first_col = row.find_all('td')[0].get_text(strip=True)
            if first_col.isdigit():
                serial_numbers.append(int(first_col))

        if serial_numbers:
            unique_count = len(set(serial_numbers))
            print(f"📊 Latest total (unique serial numbers): {unique_count}")
            return unique_count

        count = len(data_rows)
        print(f"📊 Latest total (row count): {count}")
        return count

    def fetch_basic_records(self):
        """Retrieve the current basic pharmacist listing from the council website"""
        total_url = "https://www.pharmacycouncil.telangana.gov.in/pharmacy/srchpharmacisttotal"
        print("🌐 Fetching pharmacist listing for sync...")
        response = self.make_request(total_url)
        if not response:
            print("⚠️  Unable to retrieve the total pharmacists page.")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')

        table = soup.find('table', attrs={'id': 'tablesorter-demo'})
        if not table:
            tables = soup.find_all('table')
            table = tables[0] if tables else None

        if not table:
            print("❓ Could not locate the pharmacists table on the page.")
            return []

        rows = table.find_all('tr')
        if not rows:
            print("❓ No pharmacist rows found in the table.")
            return []

        records = []
        for row in rows[1:]:
            cells = row.find_all('td')
            if len(cells) < 5:
                continue

            serial_text = cells[0].get_text(strip=True)
            reg_no = cells[1].get_text(strip=True)
            name = cells[2].get_text(strip=True)
            father_name = cells[3].get_text(strip=True)
            category = cells[4].get_text(strip=True)

            record = {
                "serial_number": int(serial_text) if serial_text.isdigit() else serial_text,
                "registration_number": reg_no,
                "name": name,
                "father_name": father_name,
                "category": category,
            }
            records.append(record)

        print(f"📥 Retrieved {len(records)} basic records from the council website")
        return records

    def extract_detailed_info(self, reg_number):
        """Extract detailed information for a single registration number"""
        # Use the correct endpoint discovered through testing
        search_url = "https://www.pharmacycouncil.telangana.gov.in/pharmacy/getsearchpharmacist"

        form_data = {
            'registration_no': reg_number,  # Only registration number
            'app_name': '',                # Leave empty as instructed
            'father_name': '',             # Leave empty as instructed
            'dob': '',                     # Leave empty as instructed
            'submit': 'Submit'
        }

        response = self.make_request(search_url, form_data)
        if not response:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract ONLY the data that appears on the search results page
        detailed_info = {}

        tables = soup.find_all('table')

        if len(tables) >= 1:
            # Table 1: "Pharmacist Info" section
            main_table = tables[0]
            rows = main_table.find_all('tr')

            if len(rows) >= 2:  # Header + data row
                data_row = rows[1]  # Second row contains the data
                cols = data_row.find_all('td')

                if len(cols) >= 7:  # We expect at least 7 columns
                    # Extract using EXACT field names from the website headers
                    header_row = rows[0]
                    headers = header_row.find_all(['th', 'td'])

                    # Map each column to its exact header name
                    for i, header in enumerate(headers):
                        header_text = header.text.strip()
                        if i < len(cols) and header_text:
                            col_value = cols[i].text.strip()

                            # For photo column, check if there's an image or link
                            if i == len(headers) - 1:  # Last column is typically photo
                                photo_img = cols[i].find('img')
                                if photo_img:
                                    # Check if it's base64 encoded (data:image format)
                                    src_attr = photo_img.get('src', '')
                                    if src_attr and 'data:image' in src_attr:
                                        # Base64 encoded image - include as-is
                                        final_value = src_attr
                                    elif src_attr and re.search(r'[a-zA-Z0-9]', src_attr):
                                        # Regular URL with alphanumeric content - include as-is
                                        final_value = src_attr
                                    else:
                                        # Empty or no content
                                        final_value = col_value
                                else:
                                    photo_link = cols[i].find('a')
                                    if photo_link:
                                        final_value = photo_link.get('href', '')
                                    else:
                                        final_value = col_value
                            else:
                                final_value = col_value

                            # WORKAROUND: Check for alphanumeric content (including base64)
                            if final_value and re.search(r'[a-zA-Z0-9]', final_value):
                                # Has alphanumeric characters - include as-is
                                detailed_info[header_text] = final_value
                            elif header_text:
                                # No alphanumeric characters - mark as NA
                                detailed_info[header_text] = 'NA'

        if len(tables) >= 2:
            # Table 2: "Academic Information" section
            edu_table = tables[1]
            edu_rows = edu_table.find_all('tr')

            if len(edu_rows) >= 2:
                edu_data = edu_rows[1]
                edu_cols = edu_data.find_all('td')

                if len(edu_cols) >= 7:
                    # Get education table headers
                    edu_header_row = edu_rows[0]
                    edu_headers = edu_header_row.find_all(['th', 'td'])

                    # Map education data to exact headers
                    for i, header in enumerate(edu_headers):
                        header_text = header.text.strip()
                        if i < len(edu_cols) and header_text:
                            edu_value = edu_cols[i].text.strip()

                            # WORKAROUND: Check for alphanumeric content
                            if edu_value and re.search(r'[a-zA-Z0-9]', edu_value):
                                # Has alphanumeric characters - include as-is
                                detailed_info[header_text] = edu_value
                            elif header_text:
                                # No alphanumeric characters - mark as NA
                                detailed_info[header_text] = 'NA'

        if len(tables) >= 3:
            # Table 3: "Working / Studying Information" section
            addr_table = tables[2]
            addr_rows = addr_table.find_all('tr')

            if len(addr_rows) >= 2:
                addr_data = addr_rows[1]
                addr_cols = addr_data.find_all('td')

                if len(addr_cols) >= 4:
                    # Get address table headers
                    addr_header_row = addr_rows[0]
                    addr_headers = addr_header_row.find_all(['th', 'td'])

                    # Map address data to exact headers
                    for i, header in enumerate(addr_headers):
                        header_text = header.text.strip()
                        if i < len(addr_cols) and header_text:
                            addr_value = addr_cols[i].text.strip()

                            # WORKAROUND: Check for alphanumeric content
                            if addr_value and re.search(r'[a-zA-Z0-9]', addr_value):
                                # Has alphanumeric characters - include as-is
                                detailed_info[header_text] = addr_value
                            elif header_text:
                                # No alphanumeric characters - mark as NA
                                detailed_info[header_text] = 'NA'

        # Return only if we have actual data from the page
        if detailed_info:
            return detailed_info
        else:
            return None

    def process_batch(self, reg_numbers, start_index=0):
        """Process a batch of registration numbers"""
        progress = self.load_progress()
        completed = progress['completed']
        failed = progress['failed']

        print(f"🚀 Starting from index {start_index}")
        print(f"📊 Already completed: {len(completed)}")
        print(f"❌ Failed: {len(failed)}")

        for i, reg_number in enumerate(reg_numbers[start_index:], start_index):
            print(f"\n🔍 Processing {i+1}/{len(reg_numbers)}: {reg_number}")

            # Check if already processed
            if reg_number in completed or reg_number in failed:
                print(f"⏭️  Already processed, skipping...")
                continue

            detailed_info = self.extract_detailed_info(reg_number)

            if detailed_info:
                # Save individual record immediately
                self.save_detailed_record(detailed_info)
                completed.append(reg_number)
                print(f"✅ Successfully extracted: {reg_number}")
            else:
                failed.append(reg_number)
                print(f"❌ Failed to extract: {reg_number}")

            # Save progress every 10 requests
            if i % 10 == 0:
                self.save_progress(completed, failed, i)

            # Take longer break every 100 requests
            if i % self.long_break_after == 0 and i > 0:
                print(f"😴 Taking a {self.long_break_duration}s break after {i} requests...")
                time.sleep(self.long_break_duration)

        # Final save
        self.save_progress(completed, failed, len(reg_numbers))

    def save_detailed_record(self, record):
        """Save individual detailed record"""
        # Append to the detailed data file
        if os.path.exists(self.enhanced_data_file):
            with open(self.enhanced_data_file, 'r') as f:
                data = json.load(f)
        else:
            data = []

        data.append(record)

        with open(self.enhanced_data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def run_with_safety_checks(self):
        """Main function with safety monitoring"""
        basic_data = self.load_existing_data()
        reg_numbers = [p['registration_number'] for p in basic_data]

        print("🛡️  Reader mode activated")
        print(f"📋 Total registration numbers to process: {len(reg_numbers)}")
        print(f"🐌 Rate limiting: {self.min_delay}-{self.max_delay}s between requests")
        print(f"💤 Long break every {self.long_break_after} requests: {self.long_break_duration}s")
        print(f"💾 Progress saved every 10 requests")

        # Ask for confirmation
        response = input("\n⚠️  This will make thousands of requests. Continue? (y/N): ")
        if response.lower() != 'y':
            print("✅ Operation cancelled safely")
            return

        start_index = int(input("Start from index (0 for beginning): ") or "0")

        print("🚀 Starting data extraction...")
        self.process_batch(reg_numbers, start_index)

        print("🎉 Extraction completed!")
        print(f"📊 Check {self.enhanced_data_file} for results")
        print(f"📈 Check {self.progress_file} for progress details")

def build_arg_parser():
    parser = argparse.ArgumentParser(
        description="Dataset reader for Telangana Pharmacy Council records"
    )
    parser.add_argument(
        "--dataset",
        default="rx.json",
        help="Path to the basic dataset JSON file (default: rx.json)",
    )
    parser.add_argument(
        "--total-only",
        action="store_true",
        help="Fetch and display only the latest total pharmacist count",
    )
    return parser


if __name__ == "__main__":
    args = build_arg_parser().parse_args()
    reader = Reader(dataset_path=args.dataset)

    if args.total_only:
        count = reader.get_total_pharmacist_count()
        if count is not None:
            print(f"✅ Total pharmacists currently listed: {count}")
        else:
            sys.exit(1)
    else:
        reader.run_with_safety_checks()
