# TGPC Data Extraction System

**Minimal pharmacist registration data extraction from TGPC**

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Usage

```bash
# Get total pharmacist count
tgpc total

# Extract basic records
tgpc extract --output data/pharmacists.json

# Extract detailed information
tgpc detailed --dataset data/pharmacists.json

# Sync with website
tgpc sync --dataset data/pharmacists.json
```

## Data

Your pharmacist data is stored in:
- **Main dataset**: `data/rx.json` (82,488+ records)

## Configuration

Copy `.env.example` to `.env` and customize if needed:

```bash
cp .env.example .env
```

## Project Structure

```
tgpc/
├── cli/           # Command-line interface
├── core/          # Core engine and exceptions
├── config/        # Configuration management
├── extractors/    # Data extraction components
├── models/        # Data models
├── storage/       # File management
└── utils/         # Logging utilities
```

## Legal Notice

This data is extracted from the public TGPC website for research and analysis purposes. Users are responsible for compliance with applicable laws and regulations.