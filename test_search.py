import requests
from bs4 import BeautifulSoup

def test_search():
    # Test with a sample registration number from our data
    test_reg_no = "TG061005"  # First registration number from our dataset

    print("🔍 TESTING SEARCH FUNCTIONALITY")
    print(f"📋 Test Registration Number: {test_reg_no}")
    print()

    search_url = "https://www.pharmacycouncil.telangana.gov.in/pharmacy/search_pharmacist"

    # First, let's see what the search page looks like
    print("📄 FETCHING SEARCH PAGE...")
    response = requests.get(search_url, timeout=30)
    print(f"📊 Response Status: {response.status_code}")
    print(f"📏 Content Length: {len(response.content)} bytes")
    print()

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Look for forms
        forms = soup.find_all('form')
        print(f"🔍 Found {len(forms)} forms on the page")

        for i, form in enumerate(forms):
            print(f"\n📝 Form {i+1}:")
            print(f"   Action: {form.get('action', 'No action')}")
            print(f"   Method: {form.get('method', 'No method')}")

            inputs = form.find_all(['input', 'select', 'textarea'])
            print(f"   Fields: {len(inputs)}")

            for j, input_field in enumerate(inputs):
                field_name = input_field.get('name', 'No name')
                field_type = input_field.get('type', 'No type')
                field_value = input_field.get('value', '')
                print(f"     Field {j+1}: {field_name} ({field_type}) = '{field_value}'")

        # Now test the actual search
        print("\n🚀 TESTING ACTUAL SEARCH...")
        print(f"   URL: {search_url}")
        print(f"   Registration: {test_reg_no}")

        form_data = {
            'reg_no': test_reg_no,
            'name': '',
            'dob': '',
            'submit': 'Search'
        }

        search_response = requests.post(search_url, data=form_data, timeout=30)
        print(f"📊 Search Response Status: {search_response.status_code}")
        print(f"📏 Search Content Length: {len(search_response.content)} bytes")

        if search_response.status_code == 200:
            search_soup = BeautifulSoup(search_response.content, 'html.parser')

            # Look for results
            tables = search_soup.find_all('table')
            print(f"📋 Found {len(tables)} tables in results")

            # Look for any text that might indicate results
            text_content = search_soup.get_text()
            print(f"📝 Text content length: {len(text_content)} characters")

            # Check if "No records found" or similar
            if "no records" in text_content.lower() or "not found" in text_content.lower():
                print("❌ No records found for this registration number")
            else:
                print("✅ Found some content - might have results!")

            # Show first few lines of text content
            lines = text_content.split('\n')
            meaningful_lines = [line.strip() for line in lines if line.strip() and len(line.strip()) > 20]
            print("\n📄 Sample content (first 10 meaningful lines):")
            for i, line in enumerate(meaningful_lines[:10]):
                print(f"   {i+1}: {line[:100]}...")

        return search_response
    else:
        print(f"❌ Failed to fetch search page: {response.status_code}")
        return None

if __name__ == "__main__":
    test_search()
