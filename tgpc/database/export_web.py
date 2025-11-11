"""Export database to web-friendly JSON."""
import json
import shutil
from pathlib import Path


def export_for_web(json_path: str = "data/rx.json", output_path: str = "web/data.json"):
    """Copy JSON data to web directory for static hosting."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Simply copy the JSON file
    shutil.copy(json_path, output_path)
    
    # Get file size
    size_mb = output_file.stat().st_size / (1024 * 1024)
    
    print(f"✅ Exported data to {output_path}")
    print(f"📦 File size: {size_mb:.2f} MB")
    
    # Load and show stats
    with open(output_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📊 Total records: {len(data):,}")
    
    categories = {}
    for record in data:
        cat = record['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print("📋 By category:")
    for cat, count in categories.items():
        print(f"  {cat}: {count:,}")


if __name__ == "__main__":
    export_for_web()
