# Telangana Pharmacy Council Data Extraction

Telangana Pharmacy Council - Complete Pharmacist Registration Data (82,207 records)

## 📊 Overview

This repository contains the complete extracted dataset of registered pharmacists from the Telangana Pharmacy Council website, along with a robust extraction system for obtaining detailed pharmacist information. The data provides comprehensive professional details for analysis and research purposes.

## 📋 Dataset Details

- **Total Records:** 82,207 pharmacists
- **Source:** [Telangana Pharmacy Council Website](https://www.pharmacycouncil.telangana.gov.in/pharmacy/srchpharmacisttotal)
- **Extraction Date:** October 2025
- **Format:** JSON (basic + detailed extraction capability)

## 🏥 Pharmacist Categories

| Category | Count | Description |
|----------|-------|-------------|
| **BPharm** | 57,187 | Bachelor of Pharmacy |
| **DPharm** | 16,084 | Diploma in Pharmacy |
| **PharmD** | 6,323 | Doctor of Pharmacy |
| **MPharm** | 2,353 | Master of Pharmacy |
| **QP** | 231 | Qualified Pharmacist |
| **QC** | 29 | Quality Control |

## 📁 Repository Structure

### `pharmacists_data.json`
Complete structured dataset in JSON format containing:
- Serial Number
- Registration Number (TS format)
- Full Name
- Father's Name
- Professional Category

**Size:** 14MB (82,207 records)

### `responsible_scraper.py`
Advanced extraction system with:
- Detailed pharmacist information extraction
- Rate limiting and anti-blocking measures
- Progress tracking and resume capability
- Base64 photo extraction
- Professional error handling

**Features:**
- Extracts complete pharmacist profiles including photos
- Handles all website data formats
- Resume capability for interrupted extractions
- Professional government data standards compliance

### `README.md`
This documentation file with project details and usage instructions.

### `.gitignore`
Git configuration for clean repository management.

## 🚀 Usage

### Basic Data Analysis
```python
import json

# Load the basic data
with open('pharmacists_data.json', 'r') as f:
    data = json.load(f)

print(f"Total pharmacists: {len(data)}")
print(f"BPharm count: {len([p for p in data if p['category'] == 'BPharm'])}")
```

### Detailed Data Extraction
```python
# Run the main extraction system
python3 responsible_scraper.py
```

This will extract detailed information for each pharmacist including:
- Complete contact information
- Academic qualifications
- Professional photos (base64 format)
- Work/study details
- All available website data

## 🔧 Technical Details

- **Language:** Python 3
- **Libraries:** BeautifulSoup, requests, json, re
- **Data Size:** 14MB JSON (82,207 basic records)
- **Extraction:** Advanced web scraping with rate limiting
- **Output:** JSON format with complete pharmacist profiles

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
