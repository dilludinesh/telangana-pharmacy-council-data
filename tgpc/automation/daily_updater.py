"""
Daily automated updater for TGPC pharmacist data.

This module provides secure, automated daily updates of the rx.json file
with comprehensive data integrity checks, duplicate validation, and error handling.
"""

import hashlib
import shutil
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

from tgpc.config.settings import Config
from tgpc.core.engine import TGPCEngine
from tgpc.models.pharmacist import PharmacistRecord
from tgpc.utils.logger import get_logger


@dataclass
class UpdateResult:
    """Result of daily update operation."""
    success: bool
    timestamp: datetime
    total_records: int
    new_records: int
    removed_records: int
    duplicates_found: int
    duplicates_removed: int
    data_integrity_score: float
    backup_created: str
    errors: List[str]
    warnings: List[str]


class DataIntegrityValidator:
    """Validates data integrity and handles duplicates."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def validate_records(self, records: List[PharmacistRecord]) -> Tuple[List[PharmacistRecord], Dict[str, Any]]:
        """
        Validate records for integrity and remove duplicates.

        Returns:
            Tuple of (clean_records, validation_report)
        """
        validation_report = {
            "total_input_records": len(records),
            "duplicates_found": 0,
            "invalid_records": 0,
            "clean_records": 0,
            "integrity_issues": []
        }

        # Track duplicates by registration number
        seen_reg_numbers: Set[str] = set()
        duplicate_reg_numbers: Set[str] = set()
        clean_records: List[PharmacistRecord] = []

        for record in records:
            try:
                # Validate individual record
                validation_errors = record.validate()
                if validation_errors:
                    validation_report["invalid_records"] += 1
                    validation_report["integrity_issues"].extend(validation_errors)
                    self.logger.warning(f"Invalid record {record.registration_number}: {validation_errors}")
                    continue

                # Check for duplicates
                if record.registration_number in seen_reg_numbers:
                    duplicate_reg_numbers.add(record.registration_number)
                    validation_report["duplicates_found"] += 1
                    self.logger.warning(f"Duplicate registration number found: {record.registration_number}")
                    continue

                seen_reg_numbers.add(record.registration_number)
                clean_records.append(record)

            except Exception as e:
                validation_report["invalid_records"] += 1
                validation_report["integrity_issues"].append(f"Record validation error: {str(e)}")
                self.logger.error(f"Error validating record: {e}")

        validation_report["clean_records"] = len(clean_records)
        validation_report["duplicates_removed"] = validation_report["duplicates_found"]

        # Calculate integrity score
        if validation_report["total_input_records"] > 0:
            integrity_score = validation_report["clean_records"] / validation_report["total_input_records"]
        else:
            integrity_score = 0.0

        validation_report["integrity_score"] = integrity_score

        self.logger.info(f"Data validation completed: {validation_report}")
        return clean_records, validation_report

    def verify_data_consistency(self, records: List[PharmacistRecord]) -> Dict[str, Any]:
        """Verify data consistency and patterns."""
        consistency_report = {
            "serial_number_gaps": [],
            "registration_number_patterns": {},
            "name_quality_issues": 0,
            "category_distribution": {},
            "data_quality_score": 0.0
        }

        # Check serial number sequence
        serial_numbers = [r.serial_number for r in records if isinstance(r.serial_number, int)]
        if serial_numbers:
            serial_numbers.sort()
            expected_sequence = list(range(1, len(serial_numbers) + 1))
            gaps = set(expected_sequence) - set(serial_numbers)
            consistency_report["serial_number_gaps"] = list(gaps)

        # Analyze registration number patterns
        reg_patterns = {}
        for record in records:
            prefix = record.registration_number[:2] if len(record.registration_number) >= 2 else "UNKNOWN"
            reg_patterns[prefix] = reg_patterns.get(prefix, 0) + 1
        consistency_report["registration_number_patterns"] = reg_patterns

        # Check name quality
        name_issues = 0
        for record in records:
            if not record.name or len(record.name.strip()) < 3:
                name_issues += 1
        consistency_report["name_quality_issues"] = name_issues

        # Category distribution
        categories = {}
        for record in records:
            categories[record.category] = categories.get(record.category, 0) + 1
        consistency_report["category_distribution"] = categories

        # Calculate overall data quality score
        total_records = len(records)
        if total_records > 0:
            quality_score = 1.0 - (name_issues / total_records)
            if consistency_report["serial_number_gaps"]:
                quality_score -= 0.1  # Penalize for gaps
            consistency_report["data_quality_score"] = max(0.0, quality_score)

        return consistency_report


class SecureBackupManager:
    """Manages secure backups with integrity verification."""

    def __init__(self, config: Config):
        self.config = config
        self.logger = get_logger(__name__)
        self.backup_dir = Path(config.data_directory) / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, source_file: Path) -> str:
        """Create a secure backup with checksum verification."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"rx_backup_{timestamp}.json"
        backup_path = self.backup_dir / backup_filename

        try:
            # Copy file
            shutil.copy2(source_file, backup_path)

            # Create checksum
            checksum = self._calculate_checksum(backup_path)
            checksum_file = backup_path.with_suffix('.json.sha256')

            with open(checksum_file, 'w') as f:
                f.write(f"{checksum}  {backup_filename}\n")

            self.logger.info(f"Backup created: {backup_path} (checksum: {checksum[:16]}...)")
            return str(backup_path)

        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            raise

    def verify_backup(self, backup_path: Path) -> bool:
        """Verify backup integrity using checksum."""
        checksum_file = backup_path.with_suffix('.json.sha256')

        if not checksum_file.exists():
            self.logger.warning(f"Checksum file not found for {backup_path}")
            return False

        try:
            # Read stored checksum
            with open(checksum_file, 'r') as f:
                stored_checksum = f.read().strip().split()[0]

            # Calculate current checksum
            current_checksum = self._calculate_checksum(backup_path)

            if stored_checksum == current_checksum:
                self.logger.info(f"Backup integrity verified: {backup_path}")
                return True
            else:
                self.logger.error(f"Backup integrity check failed: {backup_path}")
                return False

        except Exception as e:
            self.logger.error(f"Error verifying backup: {e}")
            return False

    def cleanup_old_backups(self, keep_days: int = 30):
        """Clean up backups older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=keep_days)

        for backup_file in self.backup_dir.glob("rx_backup_*.json"):
            try:
                # Extract timestamp from filename
                timestamp_str = backup_file.stem.split('_', 2)[2]  # rx_backup_TIMESTAMP
                file_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")

                if file_date < cutoff_date:
                    # Remove backup and checksum
                    backup_file.unlink()
                    checksum_file = backup_file.with_suffix('.json.sha256')
                    if checksum_file.exists():
                        checksum_file.unlink()

                    self.logger.info(f"Removed old backup: {backup_file}")

            except Exception as e:
                self.logger.warning(f"Error processing backup file {backup_file}: {e}")

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()


class DailyUpdater:
    """Main daily updater with comprehensive safety checks."""

    def __init__(self, config: Config = None):
        self.config = config or Config.load()
        self.logger = get_logger(__name__)
        self.engine = TGPCEngine(self.config)
        self.validator = DataIntegrityValidator()
        self.backup_manager = SecureBackupManager(self.config)

        # Safety thresholds
        self.max_record_change_percent = 5.0  # Max 5% change in record count
        self.min_integrity_score = 0.95  # Minimum 95% data integrity
        self.min_records_threshold = 80000  # Minimum expected records

    def perform_daily_update(self) -> UpdateResult:
        """Perform comprehensive daily update with all safety checks."""
        start_time = datetime.now()
        errors = []
        warnings = []

        self.logger.info("Starting daily TGPC data update")

        try:
            # Step 1: Load existing data
            existing_records = self._load_existing_data()
            existing_count = len(existing_records)

            # Step 2: Create backup
            backup_path = self._create_secure_backup()

            # Step 3: Extract fresh data (ONLY from Total Records URL)
            self.logger.info("Extracting fresh data from Total Records URL")
            fresh_records = self.engine.extract_basic_records()

            # Step 4: Validate and clean data
            self.logger.info("Validating data integrity and removing duplicates")
            clean_records, validation_report = self.validator.validate_records(fresh_records)

            # Step 5: Safety checks
            safety_check_result = self._perform_safety_checks(
                existing_count, len(clean_records), validation_report
            )

            if not safety_check_result["passed"]:
                errors.extend(safety_check_result["errors"])
                warnings.extend(safety_check_result["warnings"])

                # If critical safety check fails, abort update
                if safety_check_result["critical"]:
                    return UpdateResult(
                        success=False,
                        timestamp=start_time,
                        total_records=existing_count,
                        new_records=0,
                        removed_records=0,
                        duplicates_found=validation_report["duplicates_found"],
                        duplicates_removed=validation_report["duplicates_removed"],
                        data_integrity_score=validation_report["integrity_score"],
                        backup_created=backup_path,
                        errors=errors,
                        warnings=warnings
                    )

            # Step 6: Calculate changes
            changes = self._calculate_changes(existing_records, clean_records)

            # Step 7: Save updated data
            self.logger.info(f"Saving {len(clean_records)} validated records")
            self.engine.save_records(clean_records, "rx.json", basic_only=True)

            # Step 8: Verify saved data
            verification_result = self._verify_saved_data(clean_records)
            if not verification_result["success"]:
                errors.extend(verification_result["errors"])

            # Step 9: Cleanup old backups
            self.backup_manager.cleanup_old_backups()

            # Step 10: Generate consistency report
            self.validator.verify_data_consistency(clean_records)

            self.logger.info(f"Daily update completed successfully: {len(clean_records)} records")

            return UpdateResult(
                success=True,
                timestamp=start_time,
                total_records=len(clean_records),
                new_records=changes["new_records"],
                removed_records=changes["removed_records"],
                duplicates_found=validation_report["duplicates_found"],
                duplicates_removed=validation_report["duplicates_removed"],
                data_integrity_score=validation_report["integrity_score"],
                backup_created=backup_path,
                errors=errors,
                warnings=warnings
            )

        except Exception as e:
            self.logger.error(f"Daily update failed: {e}")
            errors.append(f"Update failed: {str(e)}")

            return UpdateResult(
                success=False,
                timestamp=start_time,
                total_records=0,
                new_records=0,
                removed_records=0,
                duplicates_found=0,
                duplicates_removed=0,
                data_integrity_score=0.0,
                backup_created="",
                errors=errors,
                warnings=warnings
            )

    def _load_existing_data(self) -> List[PharmacistRecord]:
        """Load existing rx.json data safely."""
        try:
            return self.engine.load_records("rx.json")
        except FileNotFoundError:
            self.logger.warning("No existing rx.json found, starting fresh")
            return []
        except Exception as e:
            self.logger.error(f"Error loading existing data: {e}")
            return []

    def _create_secure_backup(self) -> str:
        """Create secure backup of current data."""
        rx_path = Path(self.config.data_directory) / "rx.json"
        if rx_path.exists():
            return self.backup_manager.create_backup(rx_path)
        else:
            self.logger.warning("No existing rx.json to backup")
            return ""

    def _perform_safety_checks(self, existing_count: int, new_count: int, validation_report: Dict) -> Dict[str, Any]:
        """Perform comprehensive safety checks."""
        result = {
            "passed": True,
            "critical": False,
            "errors": [],
            "warnings": []
        }

        # Check 1: Minimum records threshold
        if new_count < self.min_records_threshold:
            result["passed"] = False
            result["critical"] = True
            result["errors"].append(f"Record count too low: {new_count} < {self.min_records_threshold}")

        # Check 2: Data integrity score
        if validation_report["integrity_score"] < self.min_integrity_score:
            result["passed"] = False
            result["critical"] = True
            result["errors"].append(f"Data integrity too low: {validation_report['integrity_score']:.3f} < {self.min_integrity_score}")

        # Check 3: Record count change percentage
        if existing_count > 0:
            change_percent = abs(new_count - existing_count) / existing_count * 100
            if change_percent > self.max_record_change_percent:
                result["passed"] = False
                result["critical"] = True
                result["errors"].append(f"Record count change too large: {change_percent:.1f}% > {self.max_record_change_percent}%")

        # Check 4: Duplicate validation
        if validation_report["duplicates_found"] > 0:
            result["warnings"].append(f"Found and removed {validation_report['duplicates_found']} duplicates")

        # Check 5: Invalid records
        if validation_report["invalid_records"] > 0:
            invalid_percent = validation_report["invalid_records"] / validation_report["total_input_records"] * 100
            if invalid_percent > 1.0:  # More than 1% invalid
                result["warnings"].append(f"High invalid record rate: {invalid_percent:.1f}%")

        return result

    def _calculate_changes(self, existing_records: List[PharmacistRecord], new_records: List[PharmacistRecord]) -> Dict[str, int]:
        """Calculate changes between existing and new data."""
        existing_reg_numbers = {r.registration_number for r in existing_records}
        new_reg_numbers = {r.registration_number for r in new_records}

        new_additions = new_reg_numbers - existing_reg_numbers
        removals = existing_reg_numbers - new_reg_numbers

        return {
            "new_records": len(new_additions),
            "removed_records": len(removals)
        }

    def _verify_saved_data(self, expected_records: List[PharmacistRecord]) -> Dict[str, Any]:
        """Verify that saved data matches expected data."""
        try:
            saved_records = self.engine.load_records("rx.json")

            if len(saved_records) != len(expected_records):
                return {
                    "success": False,
                    "errors": [f"Saved record count mismatch: {len(saved_records)} != {len(expected_records)}"]
                }

            # Verify registration numbers match
            expected_reg_numbers = {r.registration_number for r in expected_records}
            saved_reg_numbers = {r.registration_number for r in saved_records}

            if expected_reg_numbers != saved_reg_numbers:
                return {
                    "success": False,
                    "errors": ["Saved registration numbers don't match expected"]
                }

            return {"success": True, "errors": []}

        except Exception as e:
            return {
                "success": False,
                "errors": [f"Verification failed: {str(e)}"]
            }


def run_daily_update() -> UpdateResult:
    """Entry point for daily update process."""
    updater = DailyUpdater()
    return updater.perform_daily_update()


if __name__ == "__main__":
    # Run daily update
    result = run_daily_update()

    if result.success:
        print(f"✅ Daily update successful: {result.total_records} records")
        print(f"   New: {result.new_records}, Removed: {result.removed_records}")
        print(f"   Duplicates removed: {result.duplicates_removed}")
        print(f"   Data integrity: {result.data_integrity_score:.3f}")
    else:
        print("❌ Daily update failed:")
        for error in result.errors:
            print(f"   Error: {error}")
        for warning in result.warnings:
            print(f"   Warning: {warning}")
