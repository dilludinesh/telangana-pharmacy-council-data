
import re
from bs4 import BeautifulSoup
import json

def extract_pharmacists(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    pharmacists = []

    # Debug: Print basic info about the HTML
    print(f"HTML length: {len(html_content)}")
    print(f"Title: {soup.title.text if soup.title else 'No title'}")

    # Try to find tables
    tables = soup.find_all('table')
    print(f"Number of tables found: {len(tables)}")

    # Also try to find any elements that might contain pharmacist data
    # Look for common patterns in pharmacist listings
    text_content = soup.get_text()
    print(f"Total text length: {len(text_content)}")

    # Search for registration numbers (common pattern: numbers with specific formats)
    reg_numbers = re.findall(r'\b[A-Z0-9]{6,}\b', text_content)
    print(f"Found potential registration numbers: {len(reg_numbers)}")

    # Look for table-like structures in text
    lines = text_content.split('\n')
    data_lines = [line.strip() for line in lines if line.strip() and len(line.strip()) > 10]
    print(f"Found {len(data_lines)} non-empty lines")

    # Try to find any tabular data
    for i, line in enumerate(data_lines[:20]):  # Show first 20 lines
        print(f"Line {i}: {line[:100]}...")

    # Original table extraction (improved)
    for table in tables:
        print(f"Processing table...")
        rows = table.find_all('tr')
        print(f"Found {len(rows)} rows in table")

        for i, row in enumerate(rows[:5]):  # Show first 5 rows
            cols = row.find_all(['td', 'th'])
            print(f"Row {i}: {len(cols)} columns - {[col.text.strip()[:50] for col in cols]}")

        # Process all rows
        for row in rows[1:]:  # Skip header
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 5:  # Need at least 5 columns (S.No, RegNo, Name, Father, Category)
                serial_no = cols[0].text.strip() if len(cols) > 0 else ""
                reg_no = cols[1].text.strip() if len(cols) > 1 else ""
                name = cols[2].text.strip() if len(cols) > 2 else ""
                fathers_name = cols[3].text.strip() if len(cols) > 3 else ""
                category = cols[4].text.strip() if len(cols) > 4 else ""

                if reg_no and name:  # Only add if we have registration number and name
                    pharmacists.append({
                        "serial_number": serial_no,
                        "registration_number": reg_no,
                        "name": name,
                        "fathers_name": fathers_name,
                        "category": category
                    })

    # If no tables found, try to extract from text patterns
    if not pharmacists and data_lines:
        print("No tables found, trying text pattern extraction...")
        # Look for lines that might contain structured data
        for line in data_lines:
            # Common patterns: RegNo Name Father Category
            if re.search(r'\d+', line) and len(line.split()) >= 3:
                parts = line.split()
                if len(parts) >= 4:
                    pharmacists.append({
                        "registration_number": parts[0],
                        "name": " ".join(parts[1:3]),
                        "fathers_name": parts[3] if len(parts) > 3 else "",
                        "category": parts[4] if len(parts) > 4 else ""
                    })
                elif len(parts) >= 3:
                    pharmacists.append({
                        "registration_number": parts[0],
                        "name": parts[1],
                        "fathers_name": " ".join(parts[2:]),
                        "category": ""
                    })

    return pharmacists

# The html_content will be passed in from the shell script
# For now, I will read it from a file for testing
try:
    with open('page.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    print("Successfully read HTML file")
    pharmacists = extract_pharmacists(html_content)

    print(f"\nTotal pharmacists extracted: {len(pharmacists)}")

    # Save to JSON file
    with open('pharmacists_data.json', 'w', encoding='utf-8') as f:
        json.dump(pharmacists, f, indent=2, ensure_ascii=False)

    print("Data saved to pharmacists_data.json")

    # Also print first few results
    if pharmacists:
        print("\nFirst 5 pharmacists:")
        for i, p in enumerate(pharmacists[:5]):
            print(f"{i+1}. {p}")
    else:
        print("No pharmacist data found")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
