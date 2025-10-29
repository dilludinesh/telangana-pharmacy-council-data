#!/usr/bin/env python3
"""Daily synchronization utility for Telangana Pharmacy Council data."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from reader import Reader

DEFAULT_DATASET = Path("rx.json")
DEFAULT_AUDIT_LOG = Path("sync_audit.log")
DEFAULT_ARCHIVE_DIR = Path("archives")
AUDIT_SAMPLE_LIMIT = 5

COMPARISON_FIELDS = [
    "serial_number",
    "registration_number",
    "name",
    "father_name",
    "category",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync rx.json with the latest pharmacist listing from the council website",
    )
    parser.add_argument(
        "--dataset",
        default=str(DEFAULT_DATASET),
        help="Path to the dataset JSON file (default: rx.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Fetch and compare data without writing any changes",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Do not create a timestamped backup before writing updates",
    )
    parser.add_argument(
        "--no-archive",
        action="store_true",
        help="Skip archiving the full dataset snapshot after a successful sync",
    )
    parser.add_argument(
        "--audit-log",
        default=str(DEFAULT_AUDIT_LOG),
        help="Path to append audit entries (default: sync_audit.log)",
    )
    parser.add_argument(
        "--archive-dir",
        default=str(DEFAULT_ARCHIVE_DIR),
        help="Directory for archived dataset snapshots (default: archives)",
    )
    parser.add_argument(
        "--notify",
        action="store_true",
        help="Output a notification stub when changes are detected",
    )
    return parser.parse_args()


def ensure_backup(path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.with_name(f"{path.stem}.backup_{timestamp}{path.suffix}")
    with path.open("r", encoding="utf-8") as src, backup_path.open("w", encoding="utf-8") as dst:
        dst.write(src.read())
    return backup_path


def normalize_serial(value) -> Tuple[int, str]:
    """Return a tuple useful for sorting; numbers first, preserving original value for ties."""
    try:
        return int(value), str(value)
    except (TypeError, ValueError):
        return float("inf"), str(value)


def merge_records(existing: List[Dict], fetched: List[Dict]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Merge fetched records into the existing list.

    Returns a tuple of (updated_data, new_records, changed_records).
    """
    index_by_reg = {rec.get("registration_number"): idx for idx, rec in enumerate(existing)}
    updated = list(existing)  # shallow copy for mutation
    new_records: List[Dict] = []
    changed_records: List[Dict] = []

    for record in fetched:
        reg_no = record.get("registration_number")
        if not reg_no:
            continue

        if reg_no in index_by_reg:
            idx = index_by_reg[reg_no]
            current = updated[idx]
            if any(current.get(field) != record.get(field) for field in COMPARISON_FIELDS):
                merged = dict(current)
                merged.update(record)
                updated[idx] = merged
                changed_records.append(merged)
        else:
            new_records.append(record)
            updated.append(record)
            index_by_reg[reg_no] = len(updated) - 1

    updated.sort(key=lambda rec: normalize_serial(rec.get("serial_number")))
    return updated, new_records, changed_records


def write_dataset(path: Path, records: List[Dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
        f.write("\n")


def append_audit_entry(
    log_path: Path,
    dataset_path: Path,
    new_records: List[Dict],
    changed_records: List[Dict],
) -> Dict:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "dataset": str(dataset_path),
        "new_count": len(new_records),
        "changed_count": len(changed_records),
        "new_registrations": [
            record.get("registration_number") for record in new_records[:AUDIT_SAMPLE_LIMIT]
        ],
        "changed_registrations": [
            record.get("registration_number")
            for record in changed_records[:AUDIT_SAMPLE_LIMIT]
        ],
    }

    with log_path.open("a", encoding="utf-8") as log_file:
        json.dump(entry, log_file)
        log_file.write("\n")

    return entry


def archive_dataset(archive_dir: Path, records: List[Dict]) -> Path:
    archive_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = archive_dir / f"rx_snapshot_{timestamp}.json"
    with archive_path.open("w", encoding="utf-8") as archive_file:
        json.dump(records, archive_file)
        archive_file.write("\n")
    return archive_path


def notify_changes(entry: Dict) -> None:
    print("🔔 Notification stub — integrate with Slack, email, or another service here.")
    print("    Summary:")
    print(
        f"    - New registrations: {entry['new_count']}"
        f" (sample: {', '.join(entry['new_registrations']) or 'none'})"
    )
    print(
        f"    - Updated registrations: {entry['changed_count']}"
        f" (sample: {', '.join(entry['changed_registrations']) or 'none'})"
    )


def main() -> None:
    args = parse_args()
    dataset_path = Path(args.dataset)
    audit_log_path = Path(args.audit_log)
    archive_dir = Path(args.archive_dir)

    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    reader = Reader(dataset_path=str(dataset_path))
    existing_records = reader.load_existing_data()
    print(f"📚 Loaded {len(existing_records)} existing records from {dataset_path}")

    fetched_records = reader.fetch_basic_records()
    if not fetched_records:
        print("⚠️  No records fetched. Aborting sync.")
        return

    merged_records, new_records, changed_records = merge_records(existing_records, fetched_records)

    if not new_records and not changed_records:
        print("✅ Dataset already up-to-date. No changes needed.")
        if args.notify:
            notify_changes(
                {
                    "new_count": 0,
                    "changed_count": 0,
                    "new_registrations": [],
                    "changed_registrations": [],
                }
            )
        return

    print(f"✨ Found {len(new_records)} new registrations and {len(changed_records)} updated entries.")

    audit_entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "dataset": str(dataset_path),
        "new_count": len(new_records),
        "changed_count": len(changed_records),
        "new_registrations": [
            record.get("registration_number") for record in new_records[:AUDIT_SAMPLE_LIMIT]
        ],
        "changed_registrations": [
            record.get("registration_number")
            for record in changed_records[:AUDIT_SAMPLE_LIMIT]
        ],
    }

    if args.notify:
        notify_changes(audit_entry)

    if args.dry_run:
        print("📝 Dry-run mode: no files were written.")
        return

    if not args.no_backup:
        backup_path = ensure_backup(dataset_path)
        print(f"💾 Backup created at {backup_path}")

    write_dataset(dataset_path, merged_records)
    print(f"✅ Dataset updated at {dataset_path}")

    append_audit_entry(audit_log_path, dataset_path, new_records, changed_records)
    print(f"🗒️  Audit entry appended to {audit_log_path}")

    if not args.no_archive:
        archive_path = archive_dataset(archive_dir, merged_records)
        print(f"🗃️  Snapshot archived at {archive_path}")


if __name__ == "__main__":
    main()
