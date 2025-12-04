
import sys
import os
from unittest.mock import MagicMock, patch

# Mock supabase before importing tgpc
sys.modules['supabase'] = MagicMock()

from tgpc.scraper import Scraper

# Sample HTML that mimics the target site's structure
SAMPLE_HTML = """
<html>
<body>
<table id="tablesorter-demo">
    <thead>
        <tr><th>S.No</th><th>Reg No</th><th>Name</th><th>Father Name</th><th>Category</th></tr>
    </thead>
    <tbody>
        <tr>
            <td>1</td>
            <td>12345</td>
            <td>John Doe</td>
            <td>Richard Doe</td>
            <td>A-Category</td>
        </tr>
    </tbody>
</table>
</body>
</html>
"""

def run_sanity_check():
    print("🏥 Running Sanity Check...")
    
    # Mock the network request
    with patch('requests.Session.request') as mock_request:
        # Setup mock response
        mock_response = MagicMock()
        mock_response.content = SAMPLE_HTML.encode('utf-8')
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        # Initialize scraper
        scraper = Scraper()
        
        # Run extraction
        records = scraper.extract_basic_records()
        
        # Verify results
        if len(records) != 1:
            print(f"❌ Failed: Expected 1 record, got {len(records)}")
            sys.exit(1)
            
        r = records[0]
        if r.registration_number != "12345" or r.name != "John Doe":
            print(f"❌ Failed: Data mismatch. Got {r}")
            sys.exit(1)
            
        print("✅ Sanity Check Passed: Scraper logic is intact.")

if __name__ == "__main__":
    run_sanity_check()
