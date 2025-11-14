#!/usr/bin/env python3
"""
Update analytics in the website HTML file with current database statistics.
This script is run by GitHub Actions after updating rx.json.
"""

import json
import re
from pathlib import Path
from collections import Counter


def load_records(file_path: str) -> list:
    """Load records from rx.json file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            records = json.load(f)
        print(f"✓ Loaded {len(records)} records from {file_path}")
        return records
    except Exception as e:
        print(f"✗ Error loading records: {e}")
        return []


def calculate_statistics(records: list) -> dict:
    """Calculate statistics from records."""
    total = len(records)
    
    # Count by category
    categories = Counter(record.get('category', 'Unknown') for record in records)
    
    stats = {
        'total': total,
        'bpharm': categories.get('BPharm', 0),
        'dpharm': categories.get('DPharm', 0),
        'mpharm': categories.get('MPharm', 0),
        'pharmd': categories.get('PharmD', 0),
        'others': sum(categories.get(cat, 0) for cat in categories if cat not in ['BPharm', 'DPharm', 'MPharm', 'PharmD'])
    }
    
    return stats


def update_html_file(html_path: str, stats: dict) -> bool:
    """Update the HTML file with new statistics."""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Update total records
        html_content = re.sub(
            r'<div class="stat-value" id="totalRecords">\d{1,3}(,\d{3})*</div>',
            f'<div class="stat-value" id="totalRecords">{stats["total"]:,}</div>',
            html_content
        )
        
        # Update BPharm count
        html_content = re.sub(
            r'<div class="stat-value" id="bpharmCount">\d{1,3}(,\d{3})*</div>',
            f'<div class="stat-value" id="bpharmCount">{stats["bpharm"]:,}</div>',
            html_content
        )
        
        # Update DPharm count
        html_content = re.sub(
            r'<div class="stat-value" id="dpharmCount">\d{1,3}(,\d{3})*</div>',
            f'<div class="stat-value" id="dpharmCount">{stats["dpharm"]:,}</div>',
            html_content
        )
        
        # Update MPharm count
        html_content = re.sub(
            r'<div class="stat-value" id="mpharmCount">\d{1,3}(,\d{3})*</div>',
            f'<div class="stat-value" id="mpharmCount">{stats["mpharm"]:,}</div>',
            html_content
        )
        
        # Update PharmD count
        html_content = re.sub(
            r'<div class="stat-value" id="pharmdCount">\d{1,3}(,\d{3})*</div>',
            f'<div class="stat-value" id="pharmdCount">{stats["pharmd"]:,}</div>',
            html_content
        )
        
        # Write updated content
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ Updated {html_path} with new statistics")
        return True
        
    except Exception as e:
        print(f"✗ Error updating HTML file: {e}")
        return False


def main():
    """Main function to update analytics."""
    print("=" * 60)
    print("Updating Website Analytics")
    print("=" * 60)
    
    # Load records
    records = load_records('data/rx.json')
    if not records:
        print("✗ No records found, skipping analytics update")
        return
    
    # Calculate statistics
    stats = calculate_statistics(records)
    
    print("\n📊 Statistics:")
    print(f"  Total Records: {stats['total']:,}")
    print(f"  BPharm: {stats['bpharm']:,}")
    print(f"  DPharm: {stats['dpharm']:,}")
    print(f"  MPharm: {stats['mpharm']:,}")
    print(f"  PharmD: {stats['pharmd']:,}")
    if stats['others'] > 0:
        print(f"  Others: {stats['others']:,}")
    
    # Update HTML file
    html_path = 'docs/index.html'
    if Path(html_path).exists():
        if update_html_file(html_path, stats):
            print("\n✅ Analytics updated successfully!")
        else:
            print("\n❌ Failed to update analytics")
    else:
        print(f"\n✗ HTML file not found: {html_path}")


if __name__ == "__main__":
    main()
