# TGPC Pharmacist Registry

**Automated daily extraction of pharmacist registry data from Telangana Government Pharmacy Council (TGPC)**

## 🤖 Automatic Daily Updates

This repository **automatically updates daily** with the latest pharmacist data using GitHub Actions:

- ✅ **Runs weekdays during business hours** automatically
- ✅ **Fetches latest data** from TGPC website (Total Records only)
- ✅ **Validates and removes duplicates** automatically  
- ✅ **Syncs to Supabase cloud database** (PostgreSQL)
- ✅ **Updates `data/rx.json`** with clean data
- ✅ **Commits changes** automatically with update summary
- ✅ **Zero maintenance** required

## 📊 Current Data

- **Cloud Database**: Supabase (PostgreSQL) - 82,619+ records
- **JSON Backup**: `data/rx.json` (updated daily)
- **Fields**: `serial_number`, `registration_number`, `name`, `father_name`, `category`
- **Source**: https://www.pharmacycouncil.telangana.gov.in/pharmacy/srchpharmacisttotal

## 🔧 Manual Usage (Optional)

```bash
# Install dependencies
pip install -r requirements.txt

# Extract fresh data manually
python -m tgpc.cli.commands extract --output rx.json

# Get total count
python -m tgpc.cli.commands total

# Sync with website
python -m tgpc.cli.commands sync --dataset data/rx.json
```

## 🛡️ Data Integrity

- **Duplicate Detection**: Automatically removes duplicate registration numbers
- **Data Validation**: Validates all records for completeness and format
- **Safety Checks**: Prevents bad updates with integrity thresholds
- **Server Friendly**: Uses only Total Records URL (single request per day)

## 📁 Repository Structure

```
tgpc/
├── data/rx.json              # JSON backup (auto-updated)
├── scripts/                  # Supabase sync scripts
├── tgpc/                     # Python package
│   ├── automation/           # Daily update automation
│   ├── cli/                  # Command-line interface
│   ├── core/                 # Core engine and exceptions
│   ├── extractors/           # Data extraction logic
│   ├── models/               # Data models
│   ├── storage/              # File management
│   └── utils/                # Utilities
└── .github/workflows/        # GitHub Actions automation
```

## ⚙️ How Automation Works

1. **GitHub Actions** triggers on weekdays during business hours
2. **Extracts data** from TGPC Total Records URL only
3. **Validates integrity** and removes duplicates
4. **Syncs to Supabase** cloud database (PostgreSQL)
5. **Updates `data/rx.json`** if changes detected
6. **Commits changes** with detailed summary
7. **Pushes to repository** automatically

## 📈 Update History

Check the commit history to see weekday updates with summaries like:

```
🤖 Daily data update - 2025-11-06

📊 Update Summary:
• Total records: 82,605
• New records: 42
• Removed records: 0
• Duplicates removed: 3
• Data integrity: 0.998
```

## 🎯 Data Access

**Cloud Database (Recommended)**: Query the Supabase PostgreSQL database for real-time access
- Fast, scalable, globally accessible
- No downloads required
- Always up-to-date

**JSON Backup**: `data/rx.json` for offline use or archival purposes

Perfect for:
- Research and analysis
- Data science projects  
- Registry verification
- Trend monitoring

## ⚠️ Important Notes

- **Server Friendly**: Uses only the Total Records URL to avoid overloading the TGPC server
- **Public Data**: Only extracts publicly available registry information
- **Educational Use**: Intended for research and educational purposes
- **No Personal Data**: Contains only professional registration information

---

**🔄 This repository updates automatically - no manual intervention needed!**