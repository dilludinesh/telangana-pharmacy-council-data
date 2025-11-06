#!/usr/bin/env python3
"""
Standalone TGPC Daily Updater

This script can be run independently and will:
1. Update the rx.json file with latest data
2. Commit and push changes to git repository
3. Handle all error cases and logging

Usage:
    python3 scripts/standalone-updater.py
    
Can be scheduled with:
- Windows Task Scheduler
- macOS/Linux cron
- Any scheduling system
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from tgpc.automation.daily_updater import run_daily_update
except ImportError as e:
    print(f"❌ Failed to import TGPC modules: {e}")
    print("Make sure you're running this from the project root and dependencies are installed")
    sys.exit(1)


def log(message: str) -> None:
    """Log message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def run_git_command(command: list, description: str) -> bool:
    """Run git command and return success status."""
    try:
        result = subprocess.run(
            command, 
            cwd=project_root, 
            capture_output=True, 
            text=True, 
            check=True
        )
        log(f"✅ {description}")
        return True
    except subprocess.CalledProcessError as e:
        log(f"❌ {description} failed: {e.stderr.strip()}")
        return False
    except Exception as e:
        log(f"❌ {description} failed: {str(e)}")
        return False


def check_git_changes() -> bool:
    """Check if there are changes in rx.json."""
    try:
        result = subprocess.run(
            ["git", "diff", "--quiet", "data/rx.json"],
            cwd=project_root,
            capture_output=True
        )
        return result.returncode != 0  # Non-zero means there are changes
    except Exception:
        return False


def main():
    """Main update process."""
    log("🚀 Starting standalone TGPC daily update")
    
    # Change to project directory
    os.chdir(project_root)
    
    # Check if we're in a git repository
    if not (project_root / ".git").exists():
        log("❌ Not in a git repository")
        sys.exit(1)
    
    # Pull latest changes (optional, ignore failures)
    log("📥 Pulling latest changes from repository")
    run_git_command(["git", "pull", "origin", "main"], "Pull latest changes")
    
    # Run the daily update
    log("🔄 Running daily data update")
    
    try:
        result = run_daily_update()
        
        if result.success:
            log("✅ Update completed successfully")
            log(f"📊 Total records: {result.total_records:,}")
            log(f"🆕 New records: {result.new_records}")
            log(f"🗑️ Removed records: {result.removed_records}")
            log(f"🔍 Duplicates removed: {result.duplicates_removed}")
            log(f"📈 Data integrity: {result.data_integrity_score:.3f}")
            
            # Log warnings if any
            for warning in result.warnings:
                log(f"⚠️ Warning: {warning}")
                
        else:
            log("❌ Update failed")
            for error in result.errors:
                log(f"   Error: {error}")
            sys.exit(1)
            
    except Exception as e:
        log(f"❌ Update failed with exception: {str(e)}")
        sys.exit(1)
    
    # Check for changes
    if not check_git_changes():
        log("ℹ️ No changes detected in rx.json")
        log("🏁 Daily update completed (no commit needed)")
        return
    
    # Configure git user (if not already configured)
    subprocess.run(["git", "config", "user.email", "updater@tgpc.local"], 
                  cwd=project_root, capture_output=True)
    subprocess.run(["git", "config", "user.name", "TGPC Standalone Updater"], 
                  cwd=project_root, capture_output=True)
    
    # Add changes
    if not run_git_command(["git", "add", "data/rx.json"], "Stage changes"):
        sys.exit(1)
    
    # Create commit message
    commit_msg = f"""🤖 Daily data update - {datetime.now().strftime('%Y-%m-%d')}

📊 Update Summary:
• Total records: {result.total_records:,}
• New records: {result.new_records}
• Removed records: {result.removed_records}
• Duplicates removed: {result.duplicates_removed}
• Data integrity: {result.data_integrity_score:.3f}

🔄 Automated update using Total Records URL only
🛡️ Data validated and duplicates removed
⏰ Updated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"""
    
    # Commit changes
    if not run_git_command(["git", "commit", "-m", commit_msg], "Commit changes"):
        sys.exit(1)
    
    # Push changes
    if not run_git_command(["git", "push", "origin", "main"], "Push changes"):
        log("⚠️ Failed to push changes, but local commit was successful")
        log("You may need to push manually or check your git credentials")
        sys.exit(1)
    
    log("✅ Daily update completed successfully and pushed to repository")
    log("🏁 Update process finished")


if __name__ == "__main__":
    main()