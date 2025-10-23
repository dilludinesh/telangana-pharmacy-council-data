import json
from responsible_scraper import ResponsibleScraper

def test_enhanced_extraction():
    """Test the enhanced extraction with a few registration numbers"""

    # Load some test registration numbers
    with open('pharmacists_data.json', 'r') as f:
        basic_data = json.load(f)

    # Test with first 5 registration numbers
    test_reg_numbers = [p['registration_number'] for p in basic_data[:5]]

    scraper = ResponsibleScraper()

    print("🧪 TESTING ENHANCED EXTRACTION")
    print(f"📋 Testing with {len(test_reg_numbers)} registration numbers:")
    for reg in test_reg_numbers:
        print(f"   - {reg}")
    print()

    # Test each one
    for i, reg_number in enumerate(test_reg_numbers):
        print(f"🔍 Testing {i+1}/{len(test_reg_numbers)}: {reg_number}")

        detailed_info = scraper.extract_detailed_info(reg_number)

        if detailed_info and detailed_info.get('search_status') == 'success':
            print("   ✅ SUCCESS!")
            print(f"   📋 Name: {detailed_info.get('name', 'N/A')}")
            print(f"   👨 Father: {detailed_info.get('fathers_name', 'N/A')}")
            print(f"   ⚥ Gender: {detailed_info.get('gender', 'N/A')}")
            print(f"   📅 Validity: {detailed_info.get('validity', 'N/A')}")
            print(f"   🏥 Status: {detailed_info.get('status', 'N/A')}")
            print(f"   🎓 Education: {detailed_info.get('college_name', 'N/A')}")
            print(f"   📍 Address: {detailed_info.get('address', 'N/A')}")
        else:
            print("   ❌ No data found or error occurred")
            print(f"   📊 Status: {detailed_info.get('search_status', 'unknown') if detailed_info else 'failed'}")

        print()

    print("🎉 Test completed!")

if __name__ == "__main__":
    test_enhanced_extraction()
