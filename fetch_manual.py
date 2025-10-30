#!/usr/bin/env python3
"""
Script to manually fetch and display pharmacist details one at a time.
"""

import time
import webbrowser
from pathlib import Path

def fetch_pharmacist_details(reg_number: str) -> None:
    """Open the pharmacist search page in the default web browser with the registration number pre-filled."""
    base_url = "https://www.pharmacycouncil.telangana.gov.in/site/search_pharmacist"
    
    # Create a simple HTML form that auto-submits
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pharmacist Search</title>
        <script>
            window.onload = function() {{
                document.forms[0].submit();
            }};
        </script>
    </head>
    <body>
        <form action="{base_url}" method="post" target="_blank">
            <input type="hidden" name="registration_no" value="{reg_number}">
            <input type="hidden" name="app_name" value="">
            <input type="hidden" name="father_name" value="">
            <input type="hidden" name="dob" value="">
            <input type="hidden" name="submit" value="Submit">
            <p>If the search doesn't open automatically, please <button type="submit">click here</button>.</p>
        </form>
    </body>
    </html>
    """
    
    # Save the HTML to a temporary file
    temp_file = Path("temp_search.html")
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n🔍 Opening search for registration number: {reg_number}")
    print("   The search should open in your default web browser...")
    
    # Open the HTML file in the default browser
    webbrowser.open(f"file://{temp_file.absolute()}")
    
    # Clean up the temporary file after a short delay
    time.sleep(5)  # Give the browser time to load the page
    try:
        temp_file.unlink()
    except:
        pass

def main():
    print("🔎 TGPC - Pharmacist Details Lookup")
    print("   (Enter 'q' to quit)\n")
    
    while True:
        reg_number = input("Enter Registration Number (e.g., TS000001): ").strip()
        
        if reg_number.lower() in ['q', 'quit', 'exit']:
            print("👋 Goodbye!")
            break
            
        if not reg_number:
            print("⚠️ Please enter a registration number")
            continue
            
        fetch_pharmacist_details(reg_number)
        
        # Small delay to be nice to the server
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user")
