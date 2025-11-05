"""
Minimal file management system for TGPC data storage.
"""

import json
from pathlib import Path
from typing import List

from tgpc.config.settings import Config
from tgpc.models.pharmacist import PharmacistRecord
from tgpc.utils.logger import get_logger


class FileManager:
    """Minimal file manager for TGPC data storage."""
    
    def __init__(self, config: Config):
        """Initialize the file manager."""
        self.config = config
        self.logger = get_logger(__name__)
        
        # Ensure data directory exists
        self.data_dir = Path(config.data_directory)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def save_records(self, records: List[PharmacistRecord], filename: str, basic_only: bool = False) -> Path:
        """Save pharmacist records to JSON file."""
        if not records:
            raise ValueError("No records to save")
        
        file_path = self.data_dir / filename
        
        # Convert records to dictionaries
        if basic_only:
            data = [record.to_basic_dict() for record in records]
        else:
            data = [record.to_dict() for record in records]
        
        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Saved {len(records)} records to {file_path}")
        return file_path
    
    def load_records(self, filename: str) -> List[PharmacistRecord]:
        """Load pharmacist records from JSON file."""
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {filename}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError("JSON file must contain a list of records")
        
        records = []
        for item in data:
            try:
                record = PharmacistRecord.from_dict(item)
                records.append(record)
            except Exception as e:
                self.logger.warning(f"Skipping invalid record: {e}")
        
        self.logger.info(f"Loaded {len(records)} records from {file_path}")
        return records