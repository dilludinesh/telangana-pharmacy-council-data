# TGPC Rx

Automated system for Rx record management.

## Overview

- Daily Rx data extraction
- Validation and deduplication
- Cloud sync
- JSON backup

## Data Points

- Serial
- Registration ID
- Name
- Parent Name
- Category

## Architecture

- **Core**: Python logic
- **Auto**: GitHub Actions
- **Cloud**: Supabase
- **Web**: Search interface

## Usage

Automated execution.

## Maintenance (Zero-Touch)

This system is designed to run without supervision.

- **Updates**: Runs daily (Mon-Sun).
- **Health**: Checks website weekly (Sun).
- **Alerts**: GitHub will email you ONLY if something breaks.

### 🔧 Repair Guide (If it breaks)

The scraper relies on specific HTML structure. If the website changes, update `tgpc/scraper.py`.

**Key Selectors to Check:**
1.  **Table ID**: Currently looking for `table#tablesorter-demo`.
    - *Fix*: Update line ~105 in `scraper.py`.
2.  **Column Order**: Assumes: `[S.No, Reg No, Name, Father Name, Category]`.
    - *Fix*: Update indices in `extract_basic_records` (line ~148).

**Sanity Check:**
Run this command to verify fixes:
```bash
python tests/sanity.py
```

### Troubleshooting
If you receive a failure email:
1. Click the "View workflow run" link in the email.
2. Read the error log.
3. If the source website changed, the scraper might need updates.