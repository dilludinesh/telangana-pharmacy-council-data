"""
Automation module for TGPC data extraction system.

This module provides automated daily updates with comprehensive safety checks.
Used by GitHub Actions for automatic daily data updates.
"""

from tgpc.automation.daily_updater import DailyUpdater, UpdateResult, run_daily_update

__all__ = ["DailyUpdater", "run_daily_update", "UpdateResult"]
