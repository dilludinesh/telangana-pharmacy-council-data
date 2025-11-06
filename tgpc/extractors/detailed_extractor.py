"""
Detailed pharmacist data extractor for individual JSON files.

This module extracts detailed information for each pharmacist and saves
individual JSON files with exact website field names - nothing more, nothing less.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from tgpc.config.settings import Config
from tgpc.extractors.pharmacist_extractor import PharmacistExtractor
from tgpc.utils.logger import get_logger
from tgpc.core.exceptions import TGPCException


class DetailedExtractor:
    """
    Extracts detailed pharmacist information and saves individual JSON files.
    
    Uses exact website field names and structure - no additional metadata.
    """
    
    def __init__(self, config: Config = None):
        """Initialize the detailed extractor."""
        self.config = config or Config.load()
        self.logger = get_logger(__name__)
        self.extractor = PharmacistExtractor(self.config)
        
        # Setup directories
        self.data_dir = Path(self.config.data_directory)
        self.detailed_dir = self.data_dir / "detailed"
        self.metadata_dir = self.data_dir / "metadata"
        
        # Create directories
        self.detailed_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("Detailed extractor initialized")
    
    def load_basic_records(self) -> List[Dict[str, Any]]:
        """Load basic records from rx.json."""
        rx_file = self.data_dir / "rx.json"
        
        if not rx_file.exists():
            raise FileNotFoundError("rx.json not found. Run basic extraction first.")
        
        with open(rx_file, 'r', encoding='utf-8') as f:
            records = json.load(f)
        
        self.logger.info(f"Loaded {len(records)} basic records from rx.json")
        return records
    
    def get_extraction_status(self) -> Dict[str, Any]:
        """Get current extraction status."""
        status_file = self.metadata_dir / "extraction-status.json"
        
        if not status_file.exists():
            return {
                "total_records": 0,
                "extracted_count": 0,
                "failed_count": 0,
                "last_processed_index": -1,
                "extracted_registration_numbers": [],
                "failed_registration_numbers": []
            }
        
        with open(status_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_extraction_status(self, status: Dict[str, Any]) -> None:
        """Save extraction status."""
        status_file = self.metadata_dir / "extraction-status.json"
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2, ensure_ascii=False)
    
    def is_already_extracted(self, registration_number: str) -> bool:
        """Check if registration number is already extracted."""
        detailed_file = self.detailed_dir / f"{registration_number}.json"
        return detailed_file.exists()
    
    def extract_single_detailed_record(self, registration_number: str) -> Optional[Dict[str, Any]]:
        """
        Extract detailed information for a single registration number.
        
        Returns dictionary with exact website field names only.
        """
        try:
            # Extract detailed info using existing extractor
            detailed_record = self.extractor.extract_detailed_info(registration_number)
            
            if not detailed_record:
                self.logger.warning(f"No detailed info found for {registration_number}")
                return None
            
            # Convert to website-exact format (no metadata)
            website_data = self._convert_to_website_format(detailed_record)
            
            self.logger.debug(f"Successfully extracted detailed info for {registration_number}")
            return website_data
            
        except Exception as e:
            self.logger.error(f"Failed to extract detailed info for {registration_number}: {e}")
            return None
    
    def _convert_to_website_format(self, detailed_record) -> Dict[str, Any]:
        """
        Convert PharmacistRecord to exact website format.
        
        Includes ALL sections that exist on the website - exactly as they appear.
        Empty fields are included as empty strings to match website structure.
        """
        # Main pharmacist information (ONLY fields actually present on website)
        website_data = {
            "registration_number": detailed_record.registration_number or "",
            "name": detailed_record.name or "",
            "father_name": detailed_record.father_name or "",
            "category": detailed_record.category or "",
            "status": detailed_record.status or "",
            "gender": detailed_record.gender or "",
            "validity_date": detailed_record.validity_date.strftime('%d-%b-%Y') if detailed_record.validity_date else ""
        }
        
        # Photo (include if present)
        if detailed_record.photo_data:
            website_data["photo"] = detailed_record.photo_data
        
        # Education section (ALWAYS present on website)
        education_list = []
        if detailed_record.education:
            for edu in detailed_record.education:
                # Include ALL education fields as they appear on website
                edu_dict = {
                    "qualification": edu.qualification or "",
                    "board_university": edu.board_university or "",
                    "college_name": edu.college_name or "",
                    "college_address": edu.college_address or "",
                    "academic_year_from": edu.academic_year_from or "",
                    "academic_year_to": edu.academic_year_to or "",
                    "hallticket_no": edu.hallticket_no or ""
                }
                education_list.append(edu_dict)
        
        # Always include education section (even if empty)
        website_data["education"] = education_list
        
        # Work Experience section (ALWAYS present on website)
        work_dict = {
            "address": "",
            "state": "",
            "district": "",
            "pincode": ""
        }
        
        # Fill in work experience data if available
        if detailed_record.work_experience:
            work_dict["address"] = detailed_record.work_experience.address or ""
            work_dict["state"] = detailed_record.work_experience.state or ""
            work_dict["district"] = detailed_record.work_experience.district or ""
            work_dict["pincode"] = detailed_record.work_experience.pincode or ""
        
        # Always include work_experience section
        website_data["work_experience"] = work_dict
        
        return website_data
    
    def save_detailed_record(self, registration_number: str, detailed_data: Dict[str, Any]) -> bool:
        """Save detailed record to individual JSON file."""
        try:
            detailed_file = self.detailed_dir / f"{registration_number}.json"
            
            with open(detailed_file, 'w', encoding='utf-8') as f:
                json.dump(detailed_data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Saved detailed record: {detailed_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save detailed record for {registration_number}: {e}")
            return False
    
    def extract_batch(self, start_index: int = 0, batch_size: int = 50) -> Dict[str, Any]:
        """
        Extract detailed information for a batch of records.
        
        Args:
            start_index: Index to start from in rx.json
            batch_size: Number of records to process
            
        Returns:
            Dictionary with extraction results
        """
        self.logger.info(f"Starting batch extraction: start_index={start_index}, batch_size={batch_size}")
        
        # Load basic records and status
        basic_records = self.load_basic_records()
        status = self.get_extraction_status()
        
        # Update total records count
        status["total_records"] = len(basic_records)
        
        # Determine which records to process
        end_index = min(start_index + batch_size, len(basic_records))
        batch_records = basic_records[start_index:end_index]
        
        # Track batch results
        batch_results = {
            "processed": 0,
            "extracted": 0,
            "skipped": 0,
            "failed": 0,
            "start_index": start_index,
            "end_index": end_index - 1
        }
        
        self.logger.info(f"Processing records {start_index} to {end_index - 1} ({len(batch_records)} records)")
        
        for i, record in enumerate(batch_records):
            current_index = start_index + i
            registration_number = record["registration_number"]
            
            batch_results["processed"] += 1
            
            # Skip if already extracted
            if self.is_already_extracted(registration_number):
                self.logger.debug(f"Skipping {registration_number} (already extracted)")
                batch_results["skipped"] += 1
                continue
            
            # Extract detailed information
            self.logger.info(f"Extracting {current_index + 1}/{len(basic_records)}: {registration_number}")
            
            detailed_data = self.extract_single_detailed_record(registration_number)
            
            if detailed_data:
                # Save to individual JSON file
                if self.save_detailed_record(registration_number, detailed_data):
                    batch_results["extracted"] += 1
                    status["extracted_count"] += 1
                    status["extracted_registration_numbers"].append(registration_number)
                    self.logger.info(f"✅ Successfully extracted: {registration_number}")
                else:
                    batch_results["failed"] += 1
                    status["failed_count"] += 1
                    status["failed_registration_numbers"].append(registration_number)
                    self.logger.error(f"❌ Failed to save: {registration_number}")
            else:
                batch_results["failed"] += 1
                status["failed_count"] += 1
                status["failed_registration_numbers"].append(registration_number)
                self.logger.error(f"❌ Failed to extract: {registration_number}")
            
            # Update status
            status["last_processed_index"] = current_index
            
            # Save status every 10 records
            if (i + 1) % 10 == 0:
                self.save_extraction_status(status)
                self.logger.info(f"Progress: {batch_results['extracted']}/{batch_results['processed']} extracted")
        
        # Save final status
        self.save_extraction_status(status)
        
        # Log batch summary
        self.logger.info(f"Batch extraction completed:")
        self.logger.info(f"  Processed: {batch_results['processed']}")
        self.logger.info(f"  Extracted: {batch_results['extracted']}")
        self.logger.info(f"  Skipped: {batch_results['skipped']}")
        self.logger.info(f"  Failed: {batch_results['failed']}")
        
        return batch_results
    
    def get_next_batch_index(self) -> int:
        """Get the next index to start batch extraction from."""
        status = self.get_extraction_status()
        return status["last_processed_index"] + 1
    
    def get_extraction_summary(self) -> Dict[str, Any]:
        """Get summary of extraction progress."""
        status = self.get_extraction_status()
        
        # Count actual files
        actual_files = len(list(self.detailed_dir.glob("*.json")))
        
        summary = {
            "total_records": status["total_records"],
            "extracted_count": status["extracted_count"],
            "failed_count": status["failed_count"],
            "actual_files": actual_files,
            "progress_percentage": (status["extracted_count"] / status["total_records"] * 100) if status["total_records"] > 0 else 0,
            "last_processed_index": status["last_processed_index"],
            "remaining_records": max(0, status["total_records"] - status["last_processed_index"] - 1)
        }
        
        return summary


def extract_detailed_batch(start_index: int = None, batch_size: int = 50) -> Dict[str, Any]:
    """
    Convenience function to extract a batch of detailed records.
    
    Args:
        start_index: Index to start from (None = auto-detect next)
        batch_size: Number of records to process
        
    Returns:
        Dictionary with extraction results
    """
    extractor = DetailedExtractor()
    
    if start_index is None:
        start_index = extractor.get_next_batch_index()
    
    return extractor.extract_batch(start_index, batch_size)


def get_extraction_summary() -> Dict[str, Any]:
    """Get summary of extraction progress."""
    extractor = DetailedExtractor()
    return extractor.get_extraction_summary()


if __name__ == "__main__":
    # Test extraction
    print("🔄 Testing detailed extraction...")
    
    # Extract a small batch for testing
    result = extract_detailed_batch(start_index=0, batch_size=3)
    
    print(f"✅ Batch extraction completed:")
    print(f"  Processed: {result['processed']}")
    print(f"  Extracted: {result['extracted']}")
    print(f"  Failed: {result['failed']}")
    
    # Show summary
    summary = get_extraction_summary()
    print(f"📊 Overall progress: {summary['progress_percentage']:.1f}%")
    print(f"📁 Files created: {summary['actual_files']}")