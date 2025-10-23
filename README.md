# Telangana Pharmacy Council Data

Telangana Pharmacy Council - Extracted Pharmacist Registration Data (82,207 records)

## 📊 Overview

This repository contains the complete extracted dataset of registered pharmacists from the Telangana Pharmacy Council website. The data was scraped and processed to provide a structured, machine-readable format for analysis and research purposes.

## 📋 Dataset Details

- **Total Records:** 82,207 pharmacists
- **Source:** [Telangana Pharmacy Council Website](https://www.pharmacycouncil.telangana.gov.in/pharmacy/srchpharmacisttotal)
- **Extraction Date:** October 2025
- **Format:** JSON, HTML source

## 🏥 Pharmacist Categories

| Category | Count | Description |
|----------|-------|-------------|
| **BPharm** | 57,187 | Bachelor of Pharmacy |
| **DPharm** | 16,084 | Diploma in Pharmacy |
| **PharmD** | 6,323 | Doctor of Pharmacy |
| **MPharm** | 2,353 | Master of Pharmacy |
| **QP** | 231 | Qualified Pharmacist |
| **QC** | 29 | Quality Control |

## 📁 Files

### `pharmacists_data.json`
Complete structured dataset in JSON format containing:
- Serial Number
- Registration Number (TS format)
- Full Name
- Father's Name
- Professional Category

### `extractor.py`
Python script used for data extraction with:
- BeautifulSoup HTML parsing
- Robust error handling
- JSON export functionality

### `page.html`
Original HTML source from the pharmacy council website (66MB)

## 🚀 Usage

### Quick Analysis
```python
import json

# Load the data
with open('pharmacists_data.json', 'r') as f:
    data = json.load(f)

# Example: Count by category
categories = {}
for pharmacist in data:
    cat = pharmacist['category']
    categories[cat] = categories.get(cat, 0) + 1

print(f"BPharm pharmacists: {categories.get('BPharm', 0)}")
```

### Running the Extractor
```bash
python3 extractor.py
```

## 🔧 Technical Details

- **Language:** Python 3
- **Libraries:** BeautifulSoup, JSON, re
- **Data Size:** ~575,000 lines of JSON
- **HTML Source:** ~66MB

## 📈 Data Statistics

- **Registration Numbers:** TS000001 - TS268847 (with gaps)
- **Name Variations:** 80,000+ unique names
- **Geographic Coverage:** Telangana state, India
- **Data Completeness:** 100% (all available records)

## ⚖️ Legal Notice

This data is extracted from the public Telangana Pharmacy Council website for research and analysis purposes. Users are responsible for compliance with applicable laws and regulations regarding the use of this data.

## 🤝 Contributing

If you find issues or have improvements:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

This project is for educational and research purposes. The original data belongs to the Telangana Pharmacy Council.
