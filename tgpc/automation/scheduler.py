"""
Automated scheduler for daily TGPC data updates.

This module provides scheduling capabilities using cron-like functionality
with comprehensive error handling and monitoring.
"""

import schedule
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Callable, Dict, Any
import json

from tgpc.automation.daily_updater import run_daily_update, UpdateResult
from tgpc.config.settings import Config
from tgpc.utils.logger import get_logger


class AutomationScheduler:
    """Automated scheduler for daily TGPC updates."""
    
    def __init__(self, config: Config = None):
        self.config = config or Config.load()
        self.logger = get_logger(__name__)
        self.is_running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        
        # Schedule configuration
        self.update_time = "02:00"  # 2 AM daily
        self.max_retries = 3
        self.retry_delay_minutes = 30
        
        # Status tracking
        self.last_update: Optional[datetime] = None
        self.last_result: Optional[UpdateResult] = None
        self.status_file = Path(self.config.data_directory) / "automation_status.json"
    
    def start_scheduler(self, update_time: str = "02:00") -> None:
        """Start the automated scheduler."""
        if self.is_running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.update_time = update_time
        self.is_running = True
        
        # Schedule daily update
        schedule.clear()
        schedule.every().day.at(update_time).do(self._run_update_with_retries)
        
        self.logger.info(f"Scheduler started - daily updates at {update_time}")
        
        # Start scheduler thread
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
    
    def stop_scheduler(self) -> None:
        """Stop the automated scheduler."""
        self.is_running = False
        schedule.clear()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        self.logger.info("Scheduler stopped")
    
    def run_manual_update(self) -> UpdateResult:
        """Run manual update immediately."""
        self.logger.info("Running manual update")
        return self._run_update_with_retries()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current scheduler status."""
        return {
            "is_running": self.is_running,
            "update_time": self.update_time,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "last_result": {
                "success": self.last_result.success if self.last_result else None,
                "total_records": self.last_result.total_records if self.last_result else 0,
                "new_records": self.last_result.new_records if self.last_result else 0,
                "errors": self.last_result.errors if self.last_result else []
            } if self.last_result else None,
            "next_scheduled": self._get_next_scheduled_time()
        }
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Scheduler loop error: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _run_update_with_retries(self) -> UpdateResult:
        """Run update with retry logic."""
        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info(f"Starting daily update (attempt {attempt}/{self.max_retries})")
                
                result = run_daily_update()
                self.last_update = datetime.now()
                self.last_result = result
                
                # Save status
                self._save_status(result)
                
                if result.success:
                    self.logger.info(f"Daily update successful on attempt {attempt}")
                    self._send_success_notification(result)
                    return result
                else:
                    self.logger.error(f"Daily update failed on attempt {attempt}: {result.errors}")
                    
                    # If not the last attempt, wait and retry
                    if attempt < self.max_retries:
                        self.logger.info(f"Retrying in {self.retry_delay_minutes} minutes...")
                        time.sleep(self.retry_delay_minutes * 60)
                    else:
                        self._send_failure_notification(result)
                        return result
                        
            except Exception as e:
                self.logger.error(f"Update attempt {attempt} failed with exception: {e}")
                
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay_minutes * 60)
                else:
                    # Create failure result
                    result = UpdateResult(
                        success=False,
                        timestamp=datetime.now(),
                        total_records=0,
                        new_records=0,
                        removed_records=0,
                        duplicates_found=0,
                        duplicates_removed=0,
                        data_integrity_score=0.0,
                        backup_created="",
                        errors=[f"All {self.max_retries} attempts failed. Last error: {str(e)}"],
                        warnings=[]
                    )
                    
                    self.last_update = datetime.now()
                    self.last_result = result
                    self._save_status(result)
                    self._send_failure_notification(result)
                    return result
    
    def _save_status(self, result: UpdateResult) -> None:
        """Save automation status to file."""
        try:
            status = {
                "last_update": self.last_update.isoformat() if self.last_update else None,
                "success": result.success,
                "total_records": result.total_records,
                "new_records": result.new_records,
                "removed_records": result.removed_records,
                "duplicates_removed": result.duplicates_removed,
                "data_integrity_score": result.data_integrity_score,
                "errors": result.errors,
                "warnings": result.warnings,
                "backup_created": result.backup_created
            }
            
            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save status: {e}")
    
    def _get_next_scheduled_time(self) -> Optional[str]:
        """Get next scheduled update time."""
        if not self.is_running:
            return None
        
        try:
            jobs = schedule.get_jobs()
            if jobs:
                next_run = jobs[0].next_run
                return next_run.isoformat() if next_run else None
        except Exception:
            pass
        
        return None
    
    def _send_success_notification(self, result: UpdateResult) -> None:
        """Send success notification (can be extended for email/webhook)."""
        message = (
            f"✅ TGPC Daily Update Successful\n"
            f"Time: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Total Records: {result.total_records:,}\n"
            f"New Records: {result.new_records}\n"
            f"Removed Records: {result.removed_records}\n"
            f"Duplicates Removed: {result.duplicates_removed}\n"
            f"Data Integrity: {result.data_integrity_score:.3f}\n"
        )
        
        if result.warnings:
            message += f"Warnings: {len(result.warnings)}\n"
        
        self.logger.info(f"Update notification: {message}")
        # TODO: Add email/webhook notification here
    
    def _send_failure_notification(self, result: UpdateResult) -> None:
        """Send failure notification (can be extended for email/webhook)."""
        message = (
            f"❌ TGPC Daily Update Failed\n"
            f"Time: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Errors: {len(result.errors)}\n"
        )
        
        for error in result.errors[:3]:  # Show first 3 errors
            message += f"- {error}\n"
        
        if len(result.errors) > 3:
            message += f"... and {len(result.errors) - 3} more errors\n"
        
        self.logger.error(f"Update failure notification: {message}")
        # TODO: Add email/webhook notification here


# Global scheduler instance
_scheduler_instance: Optional[AutomationScheduler] = None


def get_scheduler() -> AutomationScheduler:
    """Get global scheduler instance."""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = AutomationScheduler()
    return _scheduler_instance


def start_daily_automation(update_time: str = "02:00") -> None:
    """Start daily automation with specified time."""
    scheduler = get_scheduler()
    scheduler.start_scheduler(update_time)


def stop_daily_automation() -> None:
    """Stop daily automation."""
    scheduler = get_scheduler()
    scheduler.stop_scheduler()


if __name__ == "__main__":
    # Example usage
    print("Starting TGPC daily automation...")
    start_daily_automation("02:00")  # 2 AM daily
    
    try:
        # Keep running
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Stopping automation...")
        stop_daily_automation()