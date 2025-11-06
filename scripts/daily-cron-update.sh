#!/bin/bash

# TGPC Daily Cron Update Script
# This script runs the daily update and commits changes automatically
# Add to crontab: 0 2 * * * /path/to/tgpc/scripts/daily-cron-update.sh

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_DIR/logs/daily-update.log"
LOCK_FILE="/tmp/tgpc-daily-update.lock"

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to cleanup on exit
cleanup() {
    rm -f "$LOCK_FILE"
}
trap cleanup EXIT

# Check if already running
if [ -f "$LOCK_FILE" ]; then
    log "❌ Another update is already running (lock file exists)"
    exit 1
fi

# Create lock file
echo $$ > "$LOCK_FILE"

log "🚀 Starting daily TGPC data update"

# Change to project directory
cd "$PROJECT_DIR"

# Check if git repo
if [ ! -d ".git" ]; then
    log "❌ Not a git repository"
    exit 1
fi

# Update repository (pull latest changes)
log "📥 Pulling latest changes from repository"
git pull origin main || {
    log "⚠️ Failed to pull latest changes, continuing with local version"
}

# Install/update dependencies
log "📦 Installing dependencies"
pip3 install -r requirements.txt --quiet || {
    log "❌ Failed to install dependencies"
    exit 1
}

# Run the daily update
log "🔄 Running daily data update"
UPDATE_OUTPUT=$(python3 -c "
from tgpc.automation.daily_updater import run_daily_update
import json

try:
    result = run_daily_update()
    
    # Create result summary
    summary = {
        'success': result.success,
        'total_records': result.total_records,
        'new_records': result.new_records,
        'removed_records': result.removed_records,
        'duplicates_removed': result.duplicates_removed,
        'integrity_score': result.data_integrity_score,
        'errors': result.errors,
        'warnings': result.warnings
    }
    
    print(json.dumps(summary))
    
except Exception as e:
    error_result = {
        'success': False,
        'total_records': 0,
        'new_records': 0,
        'removed_records': 0,
        'duplicates_removed': 0,
        'integrity_score': 0.0,
        'errors': [str(e)],
        'warnings': []
    }
    print(json.dumps(error_result))
" 2>&1)

# Parse update results
if echo "$UPDATE_OUTPUT" | tail -1 | jq -e . >/dev/null 2>&1; then
    RESULT=$(echo "$UPDATE_OUTPUT" | tail -1)
    SUCCESS=$(echo "$RESULT" | jq -r '.success')
    TOTAL_RECORDS=$(echo "$RESULT" | jq -r '.total_records')
    NEW_RECORDS=$(echo "$RESULT" | jq -r '.new_records')
    REMOVED_RECORDS=$(echo "$RESULT" | jq -r '.removed_records')
    DUPLICATES_REMOVED=$(echo "$RESULT" | jq -r '.duplicates_removed')
    INTEGRITY_SCORE=$(echo "$RESULT" | jq -r '.integrity_score')
    ERRORS=$(echo "$RESULT" | jq -r '.errors[]?' 2>/dev/null || echo "")
else
    log "❌ Failed to parse update results"
    log "Raw output: $UPDATE_OUTPUT"
    exit 1
fi

# Log results
if [ "$SUCCESS" = "true" ]; then
    log "✅ Update completed successfully"
    log "📊 Total records: $TOTAL_RECORDS"
    log "🆕 New records: $NEW_RECORDS"
    log "🗑️ Removed records: $REMOVED_RECORDS"
    log "🔍 Duplicates removed: $DUPLICATES_REMOVED"
    log "📈 Data integrity: $INTEGRITY_SCORE"
else
    log "❌ Update failed"
    if [ -n "$ERRORS" ]; then
        echo "$ERRORS" | while read -r error; do
            log "   Error: $error"
        done
    fi
    exit 1
fi

# Check for changes in rx.json
if git diff --quiet data/rx.json; then
    log "ℹ️ No changes detected in rx.json"
    log "🏁 Daily update completed (no commit needed)"
    exit 0
fi

# Commit and push changes
log "📝 Committing changes to repository"

# Configure git (if not already configured)
git config user.email "cron@$(hostname)" 2>/dev/null || true
git config user.name "TGPC Cron Updater" 2>/dev/null || true

# Add only the data file
git add data/rx.json

# Create commit message
COMMIT_MSG="🤖 Daily data update - $(date '+%Y-%m-%d')

📊 Update Summary:
• Total records: $TOTAL_RECORDS
• New records: $NEW_RECORDS
• Removed records: $REMOVED_RECORDS
• Duplicates removed: $DUPLICATES_REMOVED
• Data integrity: $INTEGRITY_SCORE

🔄 Automated update using Total Records URL only
🛡️ Data validated and duplicates removed
⏰ Updated at $(date -u '+%Y-%m-%d %H:%M:%S UTC')"

# Commit changes
git commit -m "$COMMIT_MSG" || {
    log "❌ Failed to commit changes"
    exit 1
}

# Push to repository
log "📤 Pushing changes to repository"
git push origin main || {
    log "❌ Failed to push changes to repository"
    exit 1
}

log "✅ Daily update completed successfully and pushed to repository"
log "🏁 Update process finished"

# Optional: Send notification (uncomment and configure as needed)
# curl -X POST "https://your-webhook-url.com/notify" \
#      -H "Content-Type: application/json" \
#      -d "{\"message\": \"TGPC daily update completed: $TOTAL_RECORDS records, $NEW_RECORDS new\"}"