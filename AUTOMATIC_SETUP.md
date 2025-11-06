# 🤖 Automatic Daily Updates Setup

This guide shows you how to set up **truly automatic daily updates** that run without any manual intervention, just like GitHub Actions.

## 🎯 **Option 1: GitHub Actions (Recommended)**

### **✅ Advantages:**
- ✅ **Completely automatic** - runs in the cloud
- ✅ **No server maintenance** required
- ✅ **Built-in logging** and notifications
- ✅ **Free for public repositories**
- ✅ **Automatic git commits** and pushes
- ✅ **Works from anywhere** - no local setup needed

### **Setup Steps:**

1. **Enable GitHub Actions** (already done - file created at `.github/workflows/daily-update.yml`)

2. **Configure timezone** (optional):
   ```yaml
   # Edit .github/workflows/daily-update.yml
   # Change this line to your timezone:
   - cron: '0 2 * * *'  # 2:00 AM UTC
   # Examples:
   # - cron: '0 7 * * *'  # 2:00 AM EST (UTC-5)
   # - cron: '0 6 * * *'  # 2:00 AM CST (UTC-6)
   ```

3. **Push to GitHub**:
   ```bash
   git add .github/workflows/daily-update.yml
   git commit -m "Add automatic daily updates via GitHub Actions"
   git push origin main
   ```

4. **That's it!** 🎉 
   - Updates will run **automatically every day at 2:00 AM**
   - Check the "Actions" tab in your GitHub repository to see runs
   - Data will be automatically committed and pushed

### **Manual Trigger:**
```bash
# Go to your GitHub repository → Actions → Daily TGPC Data Update → Run workflow
```

---

## 🎯 **Option 2: Cron Job (Linux/macOS)**

### **✅ Advantages:**
- ✅ **Runs on your server/computer**
- ✅ **No external dependencies**
- ✅ **Full control over timing**
- ✅ **Works offline**

### **Setup Steps:**

1. **Make script executable**:
   ```bash
   chmod +x scripts/daily-cron-update.sh
   ```

2. **Test the script**:
   ```bash
   ./scripts/daily-cron-update.sh
   ```

3. **Add to crontab**:
   ```bash
   # Open crontab editor
   crontab -e
   
   # Add this line for daily 2:00 AM updates:
   0 2 * * * /full/path/to/tgpc/scripts/daily-cron-update.sh
   
   # Examples for different times:
   # 0 2 * * *   # 2:00 AM daily
   # 30 1 * * *  # 1:30 AM daily  
   # 0 */6 * * * # Every 6 hours
   ```

4. **Verify cron job**:
   ```bash
   crontab -l  # List current cron jobs
   ```

### **Logs:**
```bash
# Check update logs
tail -f /path/to/tgpc/logs/daily-update.log
```

---

## 🎯 **Option 3: Windows Task Scheduler**

### **Setup Steps:**

1. **Open Task Scheduler** (`taskschd.msc`)

2. **Create Basic Task**:
   - Name: "TGPC Daily Update"
   - Trigger: Daily at 2:00 AM
   - Action: Start a program

3. **Configure Action**:
   - Program: `python`
   - Arguments: `scripts/standalone-updater.py`
   - Start in: `C:\path\to\tgpc`

4. **Set Additional Settings**:
   - Run whether user is logged on or not
   - Run with highest privileges
   - Configure for Windows 10

### **PowerShell Alternative:**
```powershell
# Create scheduled task via PowerShell
$action = New-ScheduledTaskAction -Execute "python" -Argument "scripts/standalone-updater.py" -WorkingDirectory "C:\path\to\tgpc"
$trigger = New-ScheduledTaskTrigger -Daily -At 2:00AM
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "TGPC Daily Update" -Action $action -Trigger $trigger -Settings $settings
```

---

## 🎯 **Option 4: Standalone Python Script**

### **✅ Advantages:**
- ✅ **Works on any platform** (Windows, macOS, Linux)
- ✅ **Simple Python script**
- ✅ **Easy to customize**
- ✅ **Can be scheduled with any system**

### **Usage:**
```bash
# Run manually
python3 scripts/standalone-updater.py

# Or make it executable and run directly
chmod +x scripts/standalone-updater.py
./scripts/standalone-updater.py
```

### **Schedule with any system:**
- **Linux/macOS**: Add to crontab
- **Windows**: Use Task Scheduler
- **Docker**: Use cron in container
- **Cloud**: Use cloud scheduler (AWS EventBridge, Google Cloud Scheduler, etc.)

---

## 🎯 **Option 5: Docker Container (Advanced)**

### **Create Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Install cron
RUN apt-get update && apt-get install -y cron git

# Add cron job
RUN echo "0 2 * * * cd /app && python3 scripts/standalone-updater.py" | crontab -

CMD ["cron", "-f"]
```

### **Run Container:**
```bash
docker build -t tgpc-updater .
docker run -d --name tgpc-daily tgpc-updater
```

---

## 📊 **Comparison of Options**

| Option | Automatic | Setup Difficulty | Maintenance | Cost | Best For |
|--------|-----------|------------------|-------------|------|----------|
| **GitHub Actions** | ✅ Yes | 🟢 Easy | 🟢 None | 🟢 Free | **Most users** |
| **Cron Job** | ✅ Yes | 🟡 Medium | 🟡 Low | 🟢 Free | Linux/macOS servers |
| **Windows Task** | ✅ Yes | 🟡 Medium | 🟡 Low | 🟢 Free | Windows users |
| **Standalone Script** | ⚠️ Manual | 🟢 Easy | 🟢 None | 🟢 Free | Custom scheduling |
| **Docker** | ✅ Yes | 🔴 Hard | 🟡 Medium | 🟢 Free | Advanced users |

---

## 🔧 **Configuration Options**

### **Update Frequency:**
```bash
# GitHub Actions (.github/workflows/daily-update.yml)
- cron: '0 2 * * *'     # Daily at 2 AM
- cron: '0 */12 * * *'  # Every 12 hours
- cron: '0 2 * * 1'     # Weekly on Monday

# Cron format: minute hour day month weekday
# 0 2 * * *   = 2:00 AM daily
# 30 1 * * *  = 1:30 AM daily
# 0 */6 * * * = Every 6 hours
# 0 2 * * 0   = 2:00 AM every Sunday
```

### **Timezone Settings:**
```bash
# For GitHub Actions, use UTC time
# Convert your local time to UTC:
# EST (UTC-5): 2 AM EST = 7 AM UTC → '0 7 * * *'
# PST (UTC-8): 2 AM PST = 10 AM UTC → '0 10 * * *'
# IST (UTC+5:30): 2 AM IST = 8:30 PM UTC → '30 20 * * *'
```

---

## 🚨 **Important Notes**

### **Data Source Rule:**
- ✅ **ONLY uses Total Records URL**: `https://www.pharmacycouncil.telangana.gov.in/pharmacy/srchpharmacisttotal`
- ❌ **NEVER uses Individual Search URL** (prevents server blocking)
- 🔄 **Single HTTP request per day** (server-friendly)

### **Safety Features:**
- 🛡️ **Automatic backup** before each update
- 🔍 **Duplicate detection** and removal
- ⚖️ **Safety thresholds** prevent bad updates
- 🔄 **Automatic rollback** on critical failures
- 📊 **Data integrity validation** (95%+ required)

### **What Gets Updated:**
- ✅ **rx.json file** with clean pharmacist data
- ✅ **Automatic git commit** with update summary
- ✅ **Push to GitHub** repository
- ❌ **No backup files** committed (kept local only)

---

## 🎯 **Recommended Setup**

### **For Most Users: GitHub Actions**
1. The `.github/workflows/daily-update.yml` file is already created
2. Just push it to your repository
3. Updates will run automatically every day
4. Check the "Actions" tab to monitor runs

### **For Servers: Cron Job**
1. Use the `scripts/daily-cron-update.sh` script
2. Add to crontab for automatic daily runs
3. Monitor logs in `logs/daily-update.log`

**🎉 Your rx.json will now update automatically every day with the latest pharmacist data!**