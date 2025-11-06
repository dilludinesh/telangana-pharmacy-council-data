# TGPC Pharmacist Registry

**Automated daily extraction of pharmacist registry data from Telangana Government Pharmacy Council (TGPC)**

## 🤖 Automatic Daily Updates

This repository **automatically updates daily** with the latest pharmacist data using GitHub Actions:

- ✅ **Runs daily at 2:00 AM UTC** automatically
- ✅ **Fetches latest data** from TGPC website (Total Records only)
- ✅ **Validates and removes duplicates** automatically  
- ✅ **Updates `data/rx.json`** with clean data
- ✅ **Commits changes** automatically with update summary
- ✅ **Zero maintenance** required

## 📊 Current Data

- **File**: `data/rx.json`
- **Records**: 82,605+ pharmacists (updated daily)
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
├── data/rx.json              # Main pharmacist dataset (auto-updated)
├── tgpc/                     # Python package
│   ├── automation/           # Daily update automation
│   ├── cli/                  # Command-line interface
│   ├── core/                 # Core engine and exceptions
│   ├── extractors/           # Data extraction logic
│   ├── models/               # Data models
│   ├── storage/              # File management
│   └── utils/                # Utilities
├── .github/workflows/        # GitHub Actions automation
└── requirements.txt          # Dependencies
```

## ⚙️ How Automation Works

1. **GitHub Actions** triggers daily at 2:00 AM UTC
2. **Extracts data** from TGPC Total Records URL only
3. **Validates integrity** and removes duplicates
4. **Updates `data/rx.json`** if changes detected
5. **Commits changes** with detailed summary
6. **Pushes to repository** automatically

## 📈 Update History

Check the commit history to see daily updates with summaries like:

```
🤖 Daily data update - 2025-11-06

📊 Update Summary:
• Total records: 82,605
• New records: 42
• Removed records: 0
• Duplicates removed: 3
• Data integrity: 0.998
```

## 🎯 Data Usage

The `data/rx.json` file contains clean, validated pharmacist registry data that's updated daily. Perfect for:

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