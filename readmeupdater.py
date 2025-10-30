#!/usr/bin/env python3
"""Utility to refresh README.md statistics from the latest dataset."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable

DEFAULT_DATASET = Path("rx.json")
README_PATH = Path("README.md")

CATEGORY_DESCRIPTIONS: Dict[str, str] = {
    "BPharm": "Bachelor of Pharmacy",
    "DPharm": "Diploma in Pharmacy",
    "PharmD": "Doctor of Pharmacy",
    "MPharm": "Master of Pharmacy",
    "QP": "Qualified Pharmacist",
    "QC": "Quality Control",
}


def format_int(value: int) -> str:
    return f"{value:,}"


def format_size_megabytes(size_in_bytes: int) -> str:
    megabytes = size_in_bytes / (1024 ** 2)
    # Keep up to two decimals, dropping trailing zeros
    return f"{megabytes:.2f}".rstrip("0").rstrip(".")


def compute_stats(dataset_path: Path) -> Dict[str, object]:
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

    with dataset_path.open("r", encoding="utf-8") as f:
        records = json.load(f)

    total_records = len(records)
    categories = Counter(
        (record.get("category") or "Unknown").strip() or "Unknown"
        for record in records
    )

    registration_numbers = sorted(
        (
            record.get("registration_number")
            for record in records
            if isinstance(record.get("registration_number"), str)
        )
    )
    min_reg, max_reg = (None, None)
    if registration_numbers:
        min_reg = registration_numbers[0]
        max_reg = registration_numbers[-1]

    unique_names = {
        record.get("name")
        for record in records
        if isinstance(record.get("name"), str) and record.get("name")
    }

    dataset_stats = dataset_path.stat()
    size_mb = format_size_megabytes(dataset_stats.st_size)
    extracted_on = datetime.fromtimestamp(dataset_stats.st_mtime).strftime("%B %Y")

    return {
        "total_records": total_records,
        "categories": categories,
        "min_registration": min_reg,
        "max_registration": max_reg,
        "unique_names": len(unique_names),
        "size_mb": size_mb,
        "extracted_on": extracted_on,
    }


def build_category_table(categories: Counter) -> str:
    lines = [
        "| Category | Count | Description |",
        "|----------|-------|-------------|",
    ]

    # Sort by descending count, then alphabetically
    for category, count in sorted(
        categories.items(), key=lambda item: (-item[1], item[0])
    ):
        description = CATEGORY_DESCRIPTIONS.get(category, "Other / Unspecified")
        lines.append(
            f"| **{category}** | {format_int(count)} | {description} |"
        )

    return "\n".join(lines)


def replace_line(pattern: str, replacement: str, text: str) -> str:
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count == 0:
        raise ValueError(f"Could not find pattern to replace: {pattern}")
    return new_text


def replace_block(
    text: str, header_line: str, new_block: str, trailing_breaks: Iterable[str] = ("\n\n",)
) -> str:
    start = text.find(header_line)
    if start == -1:
        raise ValueError(f"Could not locate block header: {header_line}")

    # Find the end of the block, stopping at the first of the trailing markers
    end = len(text)
    for breaker in trailing_breaks:
        candidate = text.find(breaker, start)
        if candidate != -1:
            end = min(end, candidate)
    return text[:start] + new_block + text[end:]


def update_readme_contents(readme: str, stats: Dict[str, object]) -> str:
    total_records = stats["total_records"]
    size_mb = stats["size_mb"]
    extracted_on = stats["extracted_on"]
    min_reg = stats["min_registration"]
    max_reg = stats["max_registration"]
    unique_names = stats["unique_names"]

    readme = replace_line(
        r"(TGPC - Complete Pharmacist Registration Data) \([^)]+\)",
        lambda m: f"{m.group(1)} ({format_int(total_records)} records)",
        readme,
    )

    readme = replace_line(
        r"\*\*Total Records:\*\* [^\n]+",
        f"**Total Records:** {format_int(total_records)} pharmacists",
        readme,
    )

    readme = replace_line(
        r"\*\*Extraction Date:\*\* [^\n]+",
        f"**Extraction Date:** {extracted_on}",
        readme,
    )

    readme = replace_line(
        r"\*\*Size:\*\* [^\n]+",
        f"**Size:** {size_mb} MB ({format_int(total_records)} records)",
        readme,
    )

    readme = replace_line(
        r"\*\*Data Size:\*\* [^\n]+",
        f"**Data Size:** {size_mb} MB JSON ({format_int(total_records)} basic records)",
        readme,
    )

    if min_reg and max_reg:
        readme = replace_line(
            r"\*\*Registration Numbers:\*\* [^\n]+",
            f"**Registration Numbers:** {min_reg} - {max_reg} (with gaps)",
            readme,
        )

    readme = replace_line(
        r"\*\*Name Variations:\*\* [^\n]+",
        f"**Name Variations:** {format_int(unique_names)} unique names",
        readme,
    )

    category_table = build_category_table(stats["categories"])
    readme = replace_block(
        readme,
        "| Category | Count | Description |",
        category_table,
        trailing_breaks=("\n\n",),
    )

    return readme


def parse_args():
    parser = argparse.ArgumentParser(
        description="Refresh README statistics from the pharmacist dataset"
    )
    parser.add_argument(
        "--dataset",
        default=str(DEFAULT_DATASET),
        help="Path to the dataset JSON file (default: rx.json)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset_path = Path(args.dataset)
    stats = compute_stats(dataset_path)
    original = README_PATH.read_text(encoding="utf-8")
    updated = update_readme_contents(original, stats)

    if updated != original:
        README_PATH.write_text(updated, encoding="utf-8")
        print("README.md updated successfully.")
    else:
        print("README.md already up-to-date.")


if __name__ == "__main__":
    main()
