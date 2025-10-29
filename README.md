# Telangana Pharmacy Council Data Extraction

Telangana Pharmacy Council - Complete Pharmacist Registration Data (82,488 records)

## 📊 Overview

This repository contains the complete extracted dataset of registered pharmacists from the Telangana Pharmacy Council website, along with a robust extraction system for obtaining detailed pharmacist information. The data provides comprehensive professional details for analysis and research purposes.

## 📋 Dataset Details

- **Total Records:** 82,488 pharmacists
- **Source:** [Telangana Pharmacy Council Website](https://www.pharmacycouncil.telangana.gov.in/pharmacy/srchpharmacisttotal)
- **Extraction Date:** October 2025
- **Format:** JSON (basic + detailed extraction capability)

## 🏥 Pharmacist Categories

| Category | Count | Description |
|----------|-------|-------------|
| **BPharm** | 57,413 | Bachelor of Pharmacy |
| **DPharm** | 16,109 | Diploma in Pharmacy |
| **PharmD** | 6,352 | Doctor of Pharmacy |
| **MPharm** | 2,354 | Master of Pharmacy |
| **QP** | 231 | Qualified Pharmacist |
| **QC** | 29 | Quality Control |

## 📁 Repository Structure

### `rx.json`
Complete structured dataset in JSON format containing:
- Serial Number
- Registration Number (TS format)
- Full Name
- Father's Name
- Professional Category

**Size:** 13.39 MB (82,488 records)

### `reader.py`
Dataset reader with:
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

### `readmeupdater.py`
Utility script that recalculates dataset statistics and refreshes `README.md` using
the latest numbers. Accepts an optional `--dataset` argument to target alternate
JSON files.

### `rxsync.py`
Daily-friendly synchronization utility that fetches the current council listing,
compares it against `rx.json`, and inserts any new or changed registrations.
Supports `--dry-run`, `--no-backup`, `--no-archive`, audit logging, and notification
stubs for Slack/email integrations.

### `README.md`
This documentation file with project details, usage instructions, and automation tips.

### `.gitignore`
Git configuration for clean repository management.

## 🚀 Usage

### Basic Data Analysis
```python
import json

# Load the basic data
with open('rx.json', 'r') as f:
    data = json.load(f)

print(f"Total pharmacists: {len(data)}")
print(f"BPharm count: {len([p for p in data if p['category'] == 'BPharm'])}")
```

### Detailed Data Extraction
```bash
# Run the main extraction system (uses rx.json by default)
python3 reader.py

# Use a different dataset file
python3 reader.py --dataset custom.json

# Fetch only the latest total pharmacist count
python3 reader.py --total-only
```

### Makefile Shortcuts
```bash
# Display the current total count
make total

# Regenerate README statistics from the dataset
make update-readme

# Run the interactive data extraction workflow
make extract

# Fetch latest council listing and merge into rx.json
make sync
```
> Tip: Override the dataset on the fly with, for example,
> `DATASET=custom.json make total`.

#### Scheduling the sync
Add an entry to your cron configuration (or any job scheduler) to run the sync once
per day:

```
0 6 * * * cd /path/to/tgpc && make sync >> /path/to/tgpc/sync.log 2>&1
```

Adjust the schedule, repository path, and logging location to suit your environment.

You can also surface summaries in Slack/email by wiring a notifier into
`rxsync.py`'s `notify_changes` function.

This will extract detailed information for each pharmacist including:
- Complete contact information
- Academic qualifications
- Professional photos (base64 format)
- Work/study details
- All available website data

## 🔧 Technical Details

- **Language:** Python 3
- **Libraries:** BeautifulSoup, requests, json, re
- **Data Size:** 13.39 MB JSON (82,488 basic records)
- **Extraction:** Advanced web scraping with rate limiting
- **Output:** JSON format with complete pharmacist profiles

## 📈 Data Statistics

- **Registration Numbers:** TG061005 - TSDR004746 (with gaps)
- **Name Variations:** 76,982 unique names
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
