# TGPC Rx Registry

Automated data extraction and management system for pharmacist registry records.

## What It Does

This repository automatically:
- Extracts pharmacist registry data daily
- Validates and removes duplicate records
- Syncs data to a cloud database
- Maintains a JSON backup file
- Runs weekdays during business hours

## Data Structure

Each record contains:
- Serial number
- Registration number
- Name
- Father's name
- Category (BPharm, DPharm, MPharm, PharmD, etc.)

## Components

- **Python Application**: Core extraction and validation logic
- **GitHub Actions**: Automated daily updates
- **Cloud Database**: PostgreSQL storage via Supabase
- **Web Interface**: Public search interface for records
- **JSON Backup**: Local data file updated daily

## Usage

The system runs automatically. No manual intervention required.

For manual operations:
```bash
# Install dependencies
pip install -r requirements.txt

# Extract data
python -m tgpc.cli.commands extract --output rx.json

# Get total count
python -m tgpc.cli.commands total

# Sync with website
python -m tgpc.cli.commands sync --dataset data/rx.json
```

## Repository Structure

```
tgpc/
├── tgpc/              # Core application code
├── data/              # JSON data files
├── scripts/           # Database sync scripts
├── docs/              # Web interface
└── .github/           # Automation workflows
```

## Features

- ✅ Automated daily updates
- ✅ Data validation and deduplication
- ✅ Cloud database synchronization
- ✅ Public search interface
- ✅ Zero maintenance required