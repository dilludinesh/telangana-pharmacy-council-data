#!/usr/bin/env python3
"""
Test script to fetch a single pharmacist's data from TGPC website.
"""

import os
import json
import time
from pathlib import Path
import requests
from bs4 import BeautifulSoup

def extract_pharmacist_data(html_content: str, reg_number: str) -> dict:
    """Extract pharmacist data from HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    content_div = soup.find('div', {'id': 'content2'})
    
    if not content_div:
        print(f"❌ No content div found for {reg_number}")
        return None

    # Data structure that matches website's field names for API compatibility
    # but uses modern Python practices internally
    pharmacist = {
        'registration': {
            'registration_no': reg_number,  # Matches website's form field name
            'validity_date': '',           # Date when registration is valid until
            'registration_status': '',      # Active/Inactive status
            'pharmacist_category': ''       # BPharm/DPharm etc.
        },
        'personal_details': {
            'name': '',                     # Full name
            'father_name': '',              # Father's/Husband's name
            'gender': '',                   # Gender
            'photo_data': None              # Base64 encoded photo
        },
        'education': [],                   # List of education records
        'work_experience': {               # Current work details
            'address': '',
            'state': '',
            'district': '',
            'pincode': ''
        }
    }
    
    # Extract basic info from the first table
    basic_table = content_div.find('table', {'class': 'B2U-article'})
    if basic_table:
        # Find all rows in the table body
        tbody = basic_table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            if rows and len(rows) > 0:
                # The first row contains the data we need
                cells = rows[0].find_all('td')
                
                # Extract text from all cells first
                text_cols = [cell.get_text(strip=True) for cell in cells]
                
                # The photo is in the last cell
                photo_data = None
                if cells and len(cells) > 7:  # Make sure we have enough cells
                    # The photo is in the last cell (8th column, 0-based index 7)
                    photo_cell = cells[7]
                    # Look for the image tag in the cell
                    img_tag = photo_cell.find('img')
                    if img_tag and 'src' in img_tag.attrs:
                        src = img_tag['src'].strip()
                        if src.startswith('data:image'):
                            photo_data = src
                
                # Map extracted data to match website's field names
                pharmacist['registration'].update({
                    'registration_no': text_cols[0] if len(text_cols) > 0 else '',
                    'registration_status': text_cols[6] if len(text_cols) > 6 else '',  # Status is now 6th column
                    'pharmacist_category': text_cols[5] if len(text_cols) > 5 else '',  # Category is 5th column
                    'validity_date': text_cols[4] if len(text_cols) > 4 else ''         # Validity is 4th column
                })
                
                # Personal details with website's field names
                pharmacist['personal_details'].update({
                    'name': text_cols[1] if len(text_cols) > 1 else '',
                    'father_name': text_cols[2] if len(text_cols) > 2 else '',
                    'gender': text_cols[3] if len(text_cols) > 3 else '',
                    'photo_data': photo_data
                })
    
    # Extract academic information from the second table
    academic_tables = content_div.find_all('table', {'class': 'B2U-article'})
    if len(academic_tables) > 1:
        academic_table = academic_tables[1]
        rows = academic_table.find_all('tr')
        if len(rows) > 1:  # Skip header row
            for row in rows[1:]:  # Skip header
                # Extract education data matching website's field names
                cells = row.find_all(['th', 'td'])
                if cells and len(cells) >= 7:  # Ensure we have all expected columns
                    education = {
                        'qualification': cells[0].get_text(strip=True),  # e.g., BPharm, DPharm
                        'board_university': cells[1].get_text(strip=True),  # e.g., JNTU Hyderabad
                        'college_name': cells[2].get_text(strip=True),  # Full college name
                        'college_address': cells[3].get_text(strip=True),  # College location
                        'academic_year_from': cells[4].get_text(strip=True),  # Start date
                        'academic_year_to': cells[5].get_text(strip=True),   # End date
                        'hallticket_no': cells[6].get_text(strip=True)  # Registration/HT number
                    }
                    pharmacist['education'].append(education)
    
    # Extract working/studying information from the third table if exists
    if len(academic_tables) > 2:
        working_table = academic_tables[2]
        rows = working_table.find_all('tr')
        if len(rows) > 1:  # Skip header row
            # Map website's column headers to our field names
            header_mapping = {
                'address': 'work_address',
                'state': 'work_state',
                'district': 'work_district',
                'pincode': 'work_pincode'
            }
            
            # Extract headers and map them
            headers = []
            for th in rows[0].find_all('th'):
                header = th.get_text(strip=True).lower()
                headers.append(header_mapping.get(header, header))
            
            # Extract work information
            for row in rows[1:]:  # Skip header
                cols = row.find_all('td')
                work_info = {}
                for i, col in enumerate(cols):
                    if i < len(headers):
                        work_info[headers[i]] = col.get_text(strip=True)
                
                # Only update if we have valid data
                if any(work_info.values()):
                    pharmacist['work_experience'] = work_info
    
    # Check if we got any data
    if not pharmacist['personal_details'].get('full_name') and not pharmacist['education']:
        print(f"❌ No pharmacist data found for {reg_number}")
        return None
        
    return pharmacist

def fetch_pharmacist(reg_number: str) -> dict:
    """Fetch a single pharmacist's data by registration number."""
    base_url = "https://www.pharmacycouncil.telangana.gov.in"
    search_url = f"{base_url}/pharmacy/getsearchpharmacist"
    referer_url = f"{base_url}/site/search_pharmacist"
    
    # Format the registration number (ensure it's 6 digits with leading zeros)
    if not reg_number.startswith('TS'):
        reg_number = f"TS{int(reg_number):06d}"
    
    print(f"🔍 Fetching data for {reg_number}...")
    
    # Prepare form data - exactly as the website sends it
    form_data = {
        'registration_no': reg_number,
        'app_name': '',
        'father_name': '',
        'dob': '',
        'submit': 'Submit'
    }
    
    # Headers to exactly match browser request
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'DNT': '1',
        'Host': 'www.pharmacycouncil.telangana.gov.in',
        'Origin': base_url,
        'Referer': referer_url,
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    
    try:
        # Create a session to maintain cookies and handle redirects
        session = requests.Session()
        
        # First, visit the search page to get necessary cookies
        session.get(referer_url, headers=headers, timeout=30)
        
        # Update headers with any cookies that were set
        headers.update({
            'Cookie': '; '.join([f"{name}={value}" for name, value in session.cookies.get_dict().items()])
        })
        
        # Submit the form with the exact same parameters as the website
        response = session.post(
            search_url,
            data=form_data,
            headers=headers,
            timeout=30,
            allow_redirects=True,
            verify=True
        )
        response.raise_for_status()
        
        # Save raw HTML for debugging and verification
        os.makedirs('debug', exist_ok=True)
        debug_file = f'debug/{reg_number}_raw.html'
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Check for no records found message (exact match with website)
        if 'No Records Found' in response.text or 'No records found' in response.text:
            print(f"⚠️ No records found for {reg_number}")
            return None
            
        # Extract pharmacist data using our parser
        data = extract_pharmacist_data(response.text, reg_number)
        
        if not data:
            print(f"⚠️ Could not parse data for {reg_number}. Check debug file: {debug_file}")
            return None
            
        print(f"✅ Successfully fetched and parsed data for {reg_number}")
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error fetching {reg_number}: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error processing {reg_number}: {str(e)}")
        if 'response' in locals() and hasattr(response, 'text'):
            with open(f'debug/{reg_number}_error.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
        return None

def main():
    # Test with registration number 1 (will be formatted as TS000001)
    reg_number = "1"
    print(f"🚀 Testing with registration number: {reg_number}")
    
    # Create directories if they don't exist
    os.makedirs('data/raw', exist_ok=True)
    
    # Fetch and save data
    result = fetch_pharmacist(reg_number)
    
    if result:
        # Save to JSON file
        with open(f'data/raw/{reg_number.zfill(6)}.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"📝 Data saved to data/raw/{reg_number.zfill(6)}.json")
        
        # Print a summary using the new field names
        print("\n📋 Extracted Data Summary:")
        print("-"*40)
        print(f"👤 Name: {result['personal_details'].get('name')}")
        print(f"👨‍👦 Father's Name: {result['personal_details'].get('father_name')}")
        print(f"🚻 Gender: {result['personal_details'].get('gender')}")
        print(f"📝 Registration: {result['registration'].get('registration_no')}")
        print(f"📊 Status: {result['registration'].get('registration_status')}")
        print(f"📅 Validity: {result['registration'].get('validity_date')}")
        
        # Education details
        if result.get('education'):
            print("\n🎓 Education Details:")
            for edu in result['education']:
                print(f"\n  📜 {edu.get('qualification', 'N/A')}")
                print(f"  🏛️  {edu.get('college_name', 'N/A')}")
                print(f"  🎓 Board/University: {edu.get('board_university', 'N/A')}")
                print(f"  📍 {edu.get('college_address', 'N/A')}")
                print(f"  📅 {edu.get('academic_year_from', 'N/A')} to {edu.get('academic_year_to', 'N/A')}")
                print(f"  🔢 HT No: {edu.get('hallticket_no', 'N/A')}")
        
        # Work experience
        if result.get('work_experience'):
            work = result['work_experience']
            if any(work.values()):  # Only show if there's any work data
                print("\n💼 Current Work/Study:")
                if work.get('work_address'):
                    print(f"  🏢 {work.get('work_address')}")
                if work.get('work_district'):
                    print(f"  🗺️  {work.get('work_district')}, {work.get('work_state', '')}")
                if work.get('work_pincode'):
                    print(f"  📮 {work.get('work_pincode')}")
    else:
        print("❌ Failed to fetch data. Check the debug file for more information.")

if __name__ == "__main__":
    main()
