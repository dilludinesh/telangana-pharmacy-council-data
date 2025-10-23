import requests
from bs4 import BeautifulSoup

def analyze_search_results():
    # Test with the first registration number from our data
    test_reg_no = "TG061005"

    print("🔍 ANALYZING SEARCH RESULTS")
    print(f"📋 Registration Number: {test_reg_no}")
    print()

    search_url = "https://www.pharmacycouncil.telangana.gov.in/pharmacy/search_pharmacist"
    form_data = {
        'registration_no': test_reg_no,
        'app_name': '',
        'father_name': '',
        'dob': '',
        'submit': 'Submit'
    }

    print("🚀 Making search request...")
    response = requests.post(search_url, data=form_data, timeout=30)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        print("📊 SEARCH RESULTS ANALYSIS:")
        print(f"   Response Size: {len(response.content)} bytes")
        print()

        # Find all tables
        tables = soup.find_all('table')
        print(f"📋 Found {len(tables)} tables")

        for i, table in enumerate(tables):
            print(f"\n🗂️  TABLE {i+1}:")
            rows = table.find_all('tr')
            print(f"   Rows: {len(rows)}")

            if len(rows) > 0:
                # Show header
                header_row = rows[0]
                headers = header_row.find_all(['th', 'td'])
                print(f"   Columns: {len(headers)}")
                print("   Headers:", [h.text.strip() for h in headers])

                # Show first few data rows
                for j, row in enumerate(rows[1:6]):  # First 5 data rows
                    cols = row.find_all('td')
                    if cols:
                        print(f"   Row {j+1}: {[col.text.strip()[:50] for col in cols]}")

        # Look for detailed information sections
        print("\n🔍 DETAILED INFORMATION SECTIONS:")

        # Look for common data fields
        text_content = soup.get_text()

        # Check for specific information patterns
        info_indicators = [
            'Name:', 'Address:', 'Phone:', 'Email:', 'Date of Birth:',
            'Registration Date:', 'Qualification:', 'Status:', 'Mobile:',
            'District:', 'State:', 'Pincode:', 'Gender:'
        ]

        found_info = []
        for indicator in info_indicators:
            if indicator.lower() in text_content.lower():
                found_info.append(indicator)

        if found_info:
            print(f"   ✅ Found {len(found_info)} information fields:")
            for info in found_info:
                print(f"      {info}")
        else:
            print("   ❌ No specific information fields detected")

        # Look for any structured data
        print("\n📄 ALL MEANINGFUL TEXT CONTENT:")
        lines = text_content.split('\n')
        meaningful_lines = [line.strip() for line in lines if line.strip() and len(line.strip()) > 10]

        # Show lines that might contain actual data (not navigation)
        data_lines = []
        for line in meaningful_lines:
            # Skip navigation/common website text
            if not any(skip in line.lower() for skip in [
                'home', 'about', 'contact', 'official website', 'pharmacy council',
                'act & rules', 'education regulations', 'designed by', 'national informatics'
            ]):
                data_lines.append(line)

        print(f"   Found {len(data_lines)} potential data lines:")
        for i, line in enumerate(data_lines[:15]):  # Show first 15
            print(f"   {i+1}: {line}")

        # Try to extract structured information
        print("\n🧩 ATTEMPTING STRUCTURED EXTRACTION:")
        structured_data = {}

        # Look for name patterns
        name_patterns = [
            r'Name\s*:\s*(.+)', r'Applicant Name\s*:\s*(.+)', r'Pharmacist Name\s*:\s*(.+)'
        ]

        for pattern in name_patterns:
            import re
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                structured_data['name'] = match.group(1).strip()
                print(f"   ✅ Name: {structured_data['name']}")
                break

        # Look for registration details
        reg_patterns = [
            r'Registration No\s*:\s*(.+)', r'Reg\. No\s*:\s*(.+)', r'Registration\s*:\s*(.+)'
        ]

        for pattern in reg_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                structured_data['registration_number'] = match.group(1).strip()
                print(f"   ✅ Registration: {structured_data['registration_number']}")
                break

        # Look for father's name
        father_patterns = [
            r"Father's Name\s*:\s*(.+)", r"Father Name\s*:\s*(.+)", r"Father\s*:\s*(.+)"
        ]

        for pattern in father_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                structured_data['fathers_name'] = match.group(1).strip()
                print(f"   ✅ Father's Name: {structured_data['fathers_name']}")
                break

        print(f"\n📋 EXTRACTED STRUCTURED DATA: {structured_data}")

        return soup
    else:
        print(f"❌ Search failed with status: {response.status_code}")
        return None

if __name__ == "__main__":
    analyze_search_results()
