#!/usr/bin/env python3
"""Daily synchronization utility for TGPC data."""

from __future__ import annotations

import argparse
import json
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from reader import Reader

DEFAULT_DATASET = Path("rx.json")
DEFAULT_AUDIT_LOG = Path("sync_audit.log")
DEFAULT_ARCHIVE_DIR = Path("archives")
DEFAULT_SMTP_PORT = 587
AUDIT_SAMPLE_LIMIT = 5

EMAIL_ENV_VARS = {
    "email_to": "RXSYNC_EMAIL_TO",
    "email_from": "RXSYNC_EMAIL_FROM",
    "smtp_server": "RXSYNC_SMTP_SERVER",
    "smtp_port": "RXSYNC_SMTP_PORT",
    "smtp_username": "RXSYNC_SMTP_USERNAME",
    "smtp_password": "RXSYNC_SMTP_PASSWORD",
    "email_subject": "RXSYNC_EMAIL_SUBJECT",
}

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
    parser.add_argument(
        "--email-to",
        help="Email recipient (or set RXSYNC_EMAIL_TO)",
    )
    parser.add_argument(
        "--email-from",
        help="Sender email address (or set RXSYNC_EMAIL_FROM)",
    )
    parser.add_argument(
        "--smtp-server",
        help="SMTP server host (or set RXSYNC_SMTP_SERVER)",
    )
    parser.add_argument(
        "--smtp-port",
        type=int,
        help="SMTP server port (default 587 or RXSYNC_SMTP_PORT)",
    )
    parser.add_argument(
        "--smtp-username",
        help="SMTP username (or set RXSYNC_SMTP_USERNAME)",
    )
    parser.add_argument(
        "--smtp-password",
        help="SMTP password (prefer using RXSYNC_SMTP_PASSWORD env)",
    )
    parser.add_argument(
        "--email-subject",
        help="Custom email subject (or set RXSYNC_EMAIL_SUBJECT)",
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


def build_email_config(args) -> Optional[Dict[str, object]]:
    def get_value(key: str, arg_value, cast=None):
        env_value = os.getenv(EMAIL_ENV_VARS[key])
        value = arg_value if arg_value is not None else env_value
        if value is None or cast is None:
            return value
        try:
            return cast(value)
        except ValueError:
            print(f"⚠️  Invalid value for {EMAIL_ENV_VARS[key]}: {value}")
            return None

    email_to = get_value("email_to", args.email_to)
    email_from = get_value("email_from", args.email_from)
    smtp_server = get_value("smtp_server", args.smtp_server)
    smtp_port = get_value("smtp_port", args.smtp_port, int)
    smtp_username = get_value("smtp_username", args.smtp_username)
    smtp_password = get_value("smtp_password", args.smtp_password)
    email_subject = get_value("email_subject", args.email_subject)

    provided = [email_to, email_from, smtp_server, smtp_username, smtp_password]
    if not any(provided):
        return None

    missing = [
        name
        for name, value in {
            "recipient": email_to,
            "sender": email_from,
            "SMTP server": smtp_server,
            "SMTP username": smtp_username,
            "SMTP password": smtp_password,
        }.items()
        if not value
    ]
    if missing:
        print(
            "⚠️  Email notifications partially configured but missing: "
            + ", ".join(missing)
        )
        return None

    return {
        "email_to": email_to,
        "email_from": email_from,
        "smtp_server": smtp_server,
        "smtp_port": smtp_port or DEFAULT_SMTP_PORT,
        "smtp_username": smtp_username,
        "smtp_password": smtp_password,
        "email_subject": email_subject,
    }


def send_email_notification(entry: Dict, summary: str, config: Dict[str, object]) -> None:
    subject_prefix = config.get("email_subject") or "Pharmacist dataset update"
    subject = (
        f"{subject_prefix}: {entry['new_count']} new, {entry['changed_count']} updated"
    )

    message = EmailMessage()
    message["From"] = config["email_from"]
    message["To"] = config["email_to"]
    message["Subject"] = subject
    message.set_content(summary)

    try:
        with smtplib.SMTP(config["smtp_server"], config["smtp_port"]) as server:
            server.starttls()
            server.login(config["smtp_username"], config["smtp_password"])
            server.send_message(message)
        print(f"📧 Email notification sent to {config['email_to']}")
    except Exception as exc:
        print(f"⚠️  Failed to send email notification: {exc}")


def notify_changes(entry: Dict, email_config: Optional[Dict[str, object]]) -> None:
    summary_lines = [
        "🔔 Notification summary:",
        f"    - New registrations: {entry['new_count']}"
        f" (sample: {', '.join(entry['new_registrations']) or 'none'})",
        f"    - Updated registrations: {entry['changed_count']}"
        f" (sample: {', '.join(entry['changed_registrations']) or 'none'})",
    ]
    summary = "\n".join(summary_lines)

    if email_config and (entry["new_count"] or entry["changed_count"]):
        send_email_notification(entry, summary, email_config)
    elif email_config:
        print("🔕 Email notification skipped (no new or updated registrations).")

    if not email_config:
        print(summary)


def main() -> None:
    args = parse_args()
    if load_dotenv is not None:
        load_dotenv()
    dataset_path = Path(args.dataset)
    audit_log_path = Path(args.audit_log)
    archive_dir = Path(args.archive_dir)
    email_config = build_email_config(args)

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
        if args.notify or email_config:
            notify_changes(
                {
                    "new_count": 0,
                    "changed_count": 0,
                    "new_registrations": [],
                    "changed_registrations": [],
                },
                email_config,
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

    if args.notify or email_config:
        notify_changes(audit_entry, email_config)

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
