# TGPC Rx Registry (Minimal Edition)

A precision-engineered system for synchronizing and displaying the Telangana State Pharmacy Council (TGPC) Pharmacist Registry.

## 🎯 Core Philosophy
**"Nothing more, nothing less."**
This project maintains a pixel-perfect, data-exact replica of the official registry's core list view. It strictly synchronizes the 5 foundational fields without extraneous metadata or enrichment.

## 📊 Data Schema
Replicates fields exactly as they appear in the source backend (snake_case):
- `registration_number`: Unique ID (e.g., TS000001)
- `name`: Pharmacist Name
- `father_name`: Father's Name
- `category`: Qualification (BPharm, DPharm, etc.)
- `serial_number`: Official S.No

## 🏗 System Architecture
- **Backend (Python)**: `tgpc` package handles scraping, deduplication (90% safety threshold), and Supabase synchronization.
- **Frontend (Static)**: `docs/index.html` provides a lightning-fast, searchable interface hosted on GitHub Pages.
- **Automation**: GitHub Actions (`.github/workflows/daily-update.yml`) runs daily to keep data fresh.

## 🚀 Setup & Usage

### Prerequisites
- Python 3.11+
- Supabase Account (optional, for search backend)

### Installation
```bash
git clone https://github.com/dilludx/tgpc.git
cd tgpc
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### Commands
```bash
# Run daily update (Scrape -> Deduplicate -> Save)
python -m tgpc update

# Sync local rx.json to Supabase
python -m tgpc sync
```

## ⚖️ License & Disclaimer
**NO LIABILITY**: The creator, the repository owner, the contributors, and the hosting platform (GitHub) assume **NO LIABILITY** and are **NOT RESPONSIBLE** for any lawsuits, damages, data loss, or legal consequences arising from the use, misuse, or existence of this repository.

- **Code**: Licensed under the MIT License.
- **Data**: All data belongs to the respective authority. This tool is for educational purposes only.
- **Usage**: Users assume full responsibility for how they use this tool and the data it accesses.

**Indian Copyright Act, 1957**: This tool is developed for educational and research purposes under the 'Fair Dealing' provisions of Section 52 of the Indian Copyright Act, 1957.
