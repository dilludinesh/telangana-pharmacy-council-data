# TGPC Daily Automation System

## 🎯 Overview

The TGPC Daily Automation System provides **secure, automated daily updates** of the pharmacist registry data (`rx.json`) with comprehensive data integrity validation, duplicate detection, and safety checks.

## 🔒 Security & Data Integrity Features

### **Data Validation**
- ✅ **Duplicate Detection**: Automatically identifies and removes duplicate registration numbers
- ✅ **Data Integrity Checks**: Validates all records against strict quality rules
- ✅ **Format Validation**: Ensures registration numbers, names, and categories meet standards
- ✅ **Consistency Verification**: Checks for data patterns and anomalies

### **Safety Mechanisms**
- 🛡️ **Change Threshold Protection**: Prevents updates if record count changes exceed 5%
- 🛡️ **Minimum Record Validation**: Ensures dataset contains at least 80,000 records
- 🛡️ **Integrity Score Requirement**: Requires 95%+ data integrity before saving
- 🛡️ **Automatic Rollback**: Restores from backup if critical safety checks fail

### **Secure Backups**
- 💾 **Automatic Backups**: Creates timestamped backups before each update
- 🔐 **Checksum Verification**: SHA-256 checksums ensure backup integrity
- 🗂️ **Retention Management**: Automatically removes backups older than 30 days
- 📁 **Organized Storage**: Backups stored in `/data/backups/` with metadata

## 🚀 Quick Start

### **Installation (Linux/macOS)**

```bash
# Clone repository
git clone https://github.com/dilludx/tgpc.git
cd tgpc

# Install dependencies
pip install -r requirements.txt

# Start daily automation (2:00 AM daily)
python -m tgpc.cli.commands automation start --time "02:00"
```

### **Production Deployment (Linux)**

```bash
# Run as root/sudo
sudo ./deployment/install.sh

# Configure environment
sudo nano /opt/tgpc/.env

# Start automation
tgpc automation start

# Check status
tgpc automation status
```

## 📋 CLI Commands

### **Automation Management**

```bash
# Start daily automation
tgpc automation start --time "02:00"

# Stop automation
tgpc automation stop

# Check status
tgpc automation status

# Run manual update
tgpc automation update

# Validate current data
tgpc automation validate
```

### **Data Operations**

```bash
# Extract fresh data (manual)
tgpc extract --output rx.json

# Get total count
tgpc total

# Sync with website
tgpc sync --dataset rx.json
```

## 🔧 Configuration

### **Environment Variables (.env)**

```bash
# API Settings
TGPC_BASE_URL=https://www.pharmacycouncil.telangana.gov.in
TGPC_TIMEOUT=30

# Rate Limiting (server-friendly)
TGPC_MIN_DELAY=4.0
TGPC_MAX_DELAY=10.0

# Data Directory
TGPC_DATA_DIRECTORY=data

# Logging
TGPC_LOG_LEVEL=INFO
```

### **Safety Thresholds**

```python
# Configurable in daily_updater.py
max_record_change_percent = 5.0    # Max 5% change
min_integrity_score = 0.95         # Min 95% integrity
min_records_threshold = 80000      # Min 80K records
```

## 📊 Data Structure

### **Clean rx.json Format**
```json
[
  {
    "serial_number": 1,
    "registration_number": "TS000001",
    "name": "Md Muzaffar Ur Rehman",
    "father_name": "Md Masoom Ali",
    "category": "BPharm"
  }
]
```

### **Only Total Records Fields**
- ✅ `serial_number` - Sequential number
- ✅ `registration_number` - Pharmacist ID (TS/TG prefix)
- ✅ `name` - Full name
- ✅ `father_name` - Father's/Husband's name  
- ✅ `category` - Qualification (BPharm, DPharm, etc.)

❌ **Excluded**: timestamps, metadata, detailed info (keeps file clean)

## 🛡️ Data Source Rules

### **CRITICAL RULE** ⚠️
- **ONLY use Total Records URL**: `https://www.pharmacycouncil.telangana.gov.in/pharmacy/srchpharmacisttotal`
- **NEVER use Individual Search URL**: Prevents server overload and blocking
- **Single Request Strategy**: One HTTP request per update (server-friendly)

## 📈 Monitoring & Alerts

### **Status Tracking**
```bash
# Real-time status
tgpc automation status

# Service logs (Linux)
journalctl -u tgpc-automation -f

# Automation status file
cat data/automation_status.json
```

### **Update Results**
```json
{
  "success": true,
  "total_records": 82605,
  "new_records": 42,
  "removed_records": 0,
  "duplicates_removed": 3,
  "data_integrity_score": 0.998,
  "backup_created": "/data/backups/rx_backup_20251105_020001.json"
}
```

## 🔄 Update Process Flow

1. **🔒 Safety Check**: Load existing data and create secure backup
2. **📥 Data Extraction**: Fetch fresh data from Total Records URL only
3. **🔍 Validation**: Remove duplicates and validate data integrity
4. **⚖️ Safety Verification**: Check change thresholds and integrity scores
5. **💾 Secure Save**: Save validated data with atomic operations
6. **✅ Verification**: Confirm saved data matches expected results
7. **🧹 Cleanup**: Remove old backups and update status

## 🚨 Error Handling

### **Automatic Recovery**
- **Retry Logic**: 3 attempts with 30-minute delays
- **Graceful Degradation**: Continues with warnings on minor issues
- **Rollback Protection**: Restores from backup on critical failures
- **Status Preservation**: Maintains last known good state

### **Common Issues & Solutions**

| Issue | Cause | Solution |
|-------|-------|----------|
| High duplicate count | Data source issues | Automatic removal + warning |
| Record count drop | Website maintenance | Safety check prevents update |
| Network timeout | Connectivity issues | Automatic retry with backoff |
| Integrity score low | Data corruption | Rollback to last good backup |

## 📁 File Structure

```
tgpc/
├── data/
│   ├── rx.json                    # Main dataset
│   ├── backups/                   # Secure backups
│   │   ├── rx_backup_*.json       # Timestamped backups
│   │   └── rx_backup_*.json.sha256 # Checksums
│   └── automation_status.json     # Status tracking
├── tgpc/automation/
│   ├── daily_updater.py          # Core update logic
│   ├── scheduler.py              # Scheduling system
│   └── __init__.py
├── deployment/
│   ├── tgpc-automation.service   # Systemd service
│   └── install.sh               # Production installer
└── AUTOMATION.md                # This documentation
```

## 🔐 Security Best Practices

### **Data Protection**
- ✅ Atomic file operations prevent corruption
- ✅ Checksum verification ensures backup integrity  
- ✅ Input validation prevents malicious data
- ✅ Rate limiting respects server resources

### **Access Control**
- ✅ Dedicated service user (production)
- ✅ Restricted file permissions
- ✅ Protected system directories
- ✅ Secure environment configuration

## 📞 Support & Troubleshooting

### **Health Checks**
```bash
# Validate current data
tgpc automation validate

# Test manual update
tgpc automation update

# Check service status
systemctl status tgpc-automation  # Linux
```

### **Recovery Procedures**
```bash
# Restore from backup
cp data/backups/rx_backup_YYYYMMDD_HHMMSS.json data/rx.json

# Verify backup integrity
sha256sum -c data/backups/rx_backup_*.json.sha256

# Reset automation
tgpc automation stop
tgpc automation start
```

## 🎯 Production Checklist

- [ ] Environment configured (`.env`)
- [ ] Service installed and enabled
- [ ] Automation started with correct time
- [ ] Initial manual update successful
- [ ] Backup directory accessible
- [ ] Log rotation configured
- [ ] Monitoring alerts set up
- [ ] Recovery procedures tested

---

**🔒 Remember**: This system is designed for **maximum data integrity and security**. All updates use only the Total Records URL to maintain server-friendly behavior while ensuring your pharmacist registry data remains accurate and up-to-date.