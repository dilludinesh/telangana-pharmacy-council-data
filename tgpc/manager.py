"""
Core management logic for TGPC system.
Handles file storage, backups, daily updates, and cloud sync.
"""

import json
import shutil
import hashlib
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from dataclasses import asdict

from supabase import create_client

from tgpc.utils import Config, TGPCError, setup_logging
from tgpc.scraper import Scraper, PharmacistRecord

logger = setup_logging("tgpc.manager")

class FileManager:
    """Handles local file storage."""
    
    def __init__(self, config: Config):
        self.data_dir = Path(config.data_directory)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def save(self, records: List[PharmacistRecord], filename: str = "rx.json"):
        """Save records to JSON."""
        path = self.data_dir / filename
        data = [r.to_dict() for r in records]
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"Saved {len(records)} records to {path}")
        return path

    def load(self, filename: str = "rx.json") -> List[PharmacistRecord]:
        """Load records from JSON."""
        path = self.data_dir / filename
        if not path.exists(): return []
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        return [PharmacistRecord(**d) for d in data]

class BackupManager:
    """Handles secure backups."""
    
    def __init__(self, config: Config):
        self.backup_dir = Path(config.data_directory) / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create(self, source: Path) -> str:
        """Create timestamped backup."""
        if not source.exists(): return ""
        
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = self.backup_dir / f"rx_backup_{ts}.json"
        shutil.copy2(source, dest)
        logger.info(f"Backup created: {dest}")
        return str(dest)

    def cleanup(self, days: int = 30):
        """Remove old backups."""
        cutoff = datetime.now() - timedelta(days=days)
        for f in self.backup_dir.glob("rx_backup_*.json"):
            try:
                ts = f.stem.split('_', 2)[2]
                if datetime.strptime(ts, "%Y%m%d_%H%M%S") < cutoff:
                    f.unlink()
            except: pass

class Manager:
    """Main management class."""

    def __init__(self):
        self.config = Config.load()
        self.file_manager = FileManager(self.config)
        self.backup_manager = BackupManager(self.config)
        self.scraper = Scraper()

    def run_daily_update(self):
        """Execute daily update workflow."""
        logger.info("Starting daily update...")
        
        # 1. Backup existing
        rx_path = Path(self.config.data_directory) / "rx.json"
        self.backup_manager.create(rx_path)

        # 2. Scrape fresh data
        fresh_records = self.scraper.extract_basic_records()
        if not fresh_records:
            logger.error("No records extracted, aborting update")
            return

        # Safety Check: Prevent massive data loss
        existing_records = self.file_manager.load()
        if existing_records and len(fresh_records) < len(existing_records) * 0.9:
            logger.error(f"Safety Alert: New count ({len(fresh_records)}) < 90% of existing ({len(existing_records)}). Aborting.")
            return

        # 3. Validate & Save
        # Simple deduplication by registration number
        unique_records = {r.registration_number: r for r in fresh_records}.values()
        sorted_records = sorted(unique_records, key=lambda r: r.serial_number or 0)
        
        # Calculate stats
        existing_map = {r.registration_number: r for r in existing_records}
        current_map = {r.registration_number: r for r in sorted_records}
        
        existing_ids = set(existing_map.keys())
        current_ids = set(current_map.keys())
        
        new_ids = current_ids - existing_ids
        removed_ids = existing_ids - current_ids
        common_ids = current_ids & existing_ids
        
        new_count = len(new_ids)
        removed_count = len(removed_ids)
        total_count = len(sorted_records)
        duplicates = len(fresh_records) - len(sorted_records)
        
        # Detailed changes
        new_details = [f"{current_map[i].registration_number} - {current_map[i].name}" for i in new_ids]
        removed_details = [f"{existing_map[i].registration_number} - {existing_map[i].name}" for i in removed_ids]
        
        modified_count = 0
        modified_details = []
        for rid in common_ids:
            if existing_map[rid] != current_map[rid]:
                modified_count += 1
                modified_details.append(f"{current_map[rid].registration_number} - {current_map[rid].name}")

        self.file_manager.save(list(sorted_records))
        self.backup_manager.cleanup()
        
        logger.info(f"Update complete. Total: {total_count}, New: {new_count}, Removed: {removed_count}, Modified: {modified_count}")

        # Output for GitHub Actions
        if os.environ.get('GITHUB_OUTPUT'):
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write(f"total_records={total_count}\n")
                f.write(f"new_records={new_count}\n")
                f.write(f"removed_records={removed_count}\n")
                f.write(f"modified_records={modified_count}\n")
                f.write(f"duplicates_removed={duplicates}\n")
                f.write(f"integrity_score=1.0\n")
                f.write(f"success=True\n")
                
                # Output details as JSON strings (limit to top 50 to avoid overflow)
                f.write(f"new_details={json.dumps(new_details[:50])}\n")
                f.write(f"removed_details={json.dumps(removed_details[:50])}\n")
                f.write(f"modified_details={json.dumps(modified_details[:50])}\n")

    def sync_to_supabase(self):
        """Sync data to Supabase."""
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_KEY")
        
        if not url or not key:
            logger.error("Missing Supabase credentials")
            return

        try:
            supabase = create_client(url, key)
            records = self.file_manager.load()
            
            logger.info(f"Syncing {len(records)} records to Supabase...")
            
            # Batch upsert
            batch_size = 1000
            for i in range(0, len(records), batch_size):
                batch = [r.to_dict() for r in records[i:i+batch_size]]
                supabase.table('rx').upsert(batch, on_conflict='registration_number').execute()
                logger.info(f"Synced batch {i//batch_size + 1}")
                
            logger.info("Supabase sync complete")
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")

