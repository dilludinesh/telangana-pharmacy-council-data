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

- **Updates**: Runs daily (Mon-Fri).
- **Health**: Checks website weekly (Sun).
- **Alerts**: GitHub will email you ONLY if something breaks.

### Troubleshooting
If you receive a failure email:
1. Click the "View workflow run" link in the email.
2. Read the error log.
3. If the source website changed, the scraper might need updates.