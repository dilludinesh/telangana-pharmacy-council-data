"""
Minimal core engine for TGPC data extraction system.
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from tgpc.config.settings import Config
from tgpc.extractors.pharmacist_extractor import PharmacistExtractor
from tgpc.storage.file_manager import FileManager
from tgpc.utils.logger import get_logger
from tgpc.models.pharmacist import PharmacistRecord
from tgpc.core.exceptions import TGPCException


class TGPCEngine:
    """Minimal engine for TGPC data extraction operations."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the TGPC engine."""
        self.config = config or Config.load()
        self.logger = get_logger(__name__)
        
        # Initialize components
        self._extractor: Optional[PharmacistExtractor] = None
        self._file_manager: Optional[FileManager] = None
        
        self.logger.info("TGPC Engine initialized")
    
    @property
    def extractor(self) -> PharmacistExtractor:
        """Get or create the pharmacist extractor."""
        if self._extractor is None:
            self._extractor = PharmacistExtractor(self.config)
        return self._extractor
    
    @property
    def file_manager(self) -> FileManager:
        """Get or create the file manager."""
        if self._file_manager is None:
            self._file_manager = FileManager(self.config)
        return self._file_manager
    
    def get_total_count(self) -> int:
        """Get the total count of pharmacists from the TGPC website."""
        self.logger.info("Fetching total pharmacist count")
        return self.extractor.extract_total_count()
    
    def extract_basic_records(self) -> List[PharmacistRecord]:
        """Extract basic pharmacist records from the TGPC website."""
        self.logger.info("Starting basic records extraction")
        raw_records = self.extractor.extract_basic_records()
        
        # Convert to PharmacistRecord objects
        records = []
        for raw_record in raw_records:
            try:
                record = PharmacistRecord.from_basic_dict(raw_record)
                records.append(record)
            except Exception as e:
                self.logger.warning(f"Failed to process record: {e}")
        
        self.logger.info(f"Basic records extraction completed: {len(records)} records")
        return records
    
    def extract_detailed_records(
        self, 
        registration_numbers: List[str],
        start_index: int = 0,
        batch_size: int = 100
    ) -> List[PharmacistRecord]:
        """Extract detailed pharmacist records for given registration numbers."""
        self.logger.info(f"Starting detailed records extraction: {len(registration_numbers)} numbers")
        
        detailed_records = self.extractor.batch_extract(
            registration_numbers[start_index:],
            batch_size=batch_size
        )
        
        self.logger.info(f"Detailed records extraction completed: {len(detailed_records)} records")
        return detailed_records
    
    def save_records(self, records: List[PharmacistRecord], filename: str) -> Path:
        """Save pharmacist records to file."""
        self.logger.info(f"Saving {len(records)} records to {filename}")
        return self.file_manager.save_records(records, filename)
    
    def load_records(self, filename: str) -> List[PharmacistRecord]:
        """Load pharmacist records from file."""
        self.logger.info(f"Loading records from {filename}")
        return self.file_manager.load_records(filename)
    
    def sync_with_website(self, existing_file: str = "pharmacists.json") -> Dict[str, Any]:
        """Synchronize local data with the TGPC website."""
        self.logger.info("Starting sync with TGPC website")
        
        # Load existing records
        existing_records = []
        existing_file_path = Path(self.config.data_directory) / existing_file
        
        if existing_file_path.exists():
            existing_records = self.load_records(existing_file)
        
        # Extract current records from website
        current_records = self.extract_basic_records()
        
        # Find new and updated records
        existing_reg_numbers = {r.registration_number for r in existing_records}
        current_reg_numbers = {r.registration_number for r in current_records}
        
        new_reg_numbers = current_reg_numbers - existing_reg_numbers
        removed_reg_numbers = existing_reg_numbers - current_reg_numbers
        
        # Save updated dataset
        if new_reg_numbers or removed_reg_numbers:
            self.save_records(current_records, existing_file)
            
            sync_result = {
                "status": "updated",
                "total_records": len(current_records),
                "new_records": len(new_reg_numbers),
                "removed_records": len(removed_reg_numbers),
            }
        else:
            sync_result = {
                "status": "no_changes",
                "total_records": len(existing_records),
                "new_records": 0,
                "removed_records": 0
            }
        
        self.logger.info("Sync completed")
        return sync_result