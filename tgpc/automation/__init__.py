"""
Automation module for TGPC data extraction system.

This module provides automated daily updates, scheduling, and monitoring
for the pharmacist registry data with comprehensive safety checks.
"""

from tgpc.automation.daily_updater import DailyUpdater, run_daily_update, UpdateResult

__all__ = ["DailyUpdater", "run_daily_update", "UpdateResult"]

# Optional scheduler (requires 'schedule' package)
try:
    from tgpc.automation.scheduler import AutomationScheduler
    __all__.append("AutomationScheduler")
except ImportError:
    AutomationScheduler = None