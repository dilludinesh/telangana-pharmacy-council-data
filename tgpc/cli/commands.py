"""
Minimal CLI commands for TGPC data extraction system.
"""

import sys
import click
from rich.console import Console

from tgpc.core.engine import TGPCEngine
from tgpc.config.settings import Config
from tgpc.core.exceptions import TGPCException

console = Console()


@click.group()
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file path")
@click.pass_context
def main(ctx, config):
    """TGPC Data Extraction System - Extract pharmacist data from TGPC website."""
    ctx.ensure_object(dict)
    ctx.obj["config_file"] = config


@main.command()
@click.pass_context
def total(ctx):
    """Get the total count of registered pharmacists."""
    try:
        config = Config.load(config_file=ctx.obj.get("config_file"))
        engine = TGPCEngine(config)
        count = engine.get_total_count()
        console.print(f"Total pharmacists: {count:,}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option("--output", "-o", default="pharmacists.json", help="Output file name")
@click.pass_context
def extract(ctx, output):
    """Extract basic pharmacist records."""
    try:
        config = Config.load(config_file=ctx.obj.get("config_file"))
        engine = TGPCEngine(config)
        
        console.print("Extracting basic records...")
        records = engine.extract_basic_records()
        
        saved_path = engine.save_records(records, output, basic_only=True)
        console.print(f"Extracted {len(records):,} records to {saved_path}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option("--start-index", "-s", type=int, help="Start index (auto-detect if not provided)")
@click.option("--batch-size", "-b", default=50, help="Number of records to extract")
@click.pass_context
def detailed(ctx, start_index, batch_size):
    """Extract detailed pharmacist information to individual JSON files."""
    try:
        from tgpc.extractors.detailed_extractor import extract_detailed_batch, get_extraction_summary
        
        console.print("🔄 Starting detailed extraction...")
        
        # Show current progress
        summary = get_extraction_summary()
        if summary["total_records"] > 0:
            console.print(f"📊 Progress: {summary['extracted_count']:,}/{summary['total_records']:,} "
                         f"({summary['progress_percentage']:.1f}%)")
        
        # Extract batch
        result = extract_detailed_batch(start_index=start_index, batch_size=batch_size)
        
        console.print(f"✅ Batch extraction completed:")
        console.print(f"  📋 Processed: {result['processed']}")
        console.print(f"  ✅ Extracted: {result['extracted']}")
        console.print(f"  ⏭️ Skipped: {result['skipped']}")
        console.print(f"  ❌ Failed: {result['failed']}")
        
        # Show updated progress
        summary = get_extraction_summary()
        console.print(f"📈 Overall progress: {summary['extracted_count']:,}/{summary['total_records']:,} "
                     f"({summary['progress_percentage']:.1f}%)")
        console.print(f"📁 Files created: {summary['actual_files']:,}")
        
        if summary['remaining_records'] > 0:
            console.print(f"⏳ Remaining: {summary['remaining_records']:,} records")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option("--dataset", "-d", default="pharmacists.json", help="Dataset file to sync")
@click.pass_context
def sync(ctx, dataset):
    """Synchronize local dataset with TGPC website."""
    try:
        config = Config.load(config_file=ctx.obj.get("config_file"))
        engine = TGPCEngine(config)
        
        console.print("Syncing with TGPC website...")
        sync_result = engine.sync_with_website(dataset)
        
        if sync_result["status"] == "no_changes":
            console.print("No changes detected")
        else:
            console.print(f"Sync complete: {sync_result['new_records']} new, {sync_result['removed_records']} removed")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command()
def status():
    """Show detailed extraction progress and statistics."""
    try:
        from tgpc.extractors.detailed_extractor import get_extraction_summary
        from rich.table import Table
        from pathlib import Path
        
        summary = get_extraction_summary()
        
        # Create status table
        table = Table(title="📊 Detailed Extraction Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Total Records", f"{summary['total_records']:,}")
        table.add_row("Extracted", f"{summary['extracted_count']:,}")
        table.add_row("Failed", f"{summary['failed_count']:,}")
        table.add_row("Progress", f"{summary['progress_percentage']:.1f}%")
        table.add_row("Files Created", f"{summary['actual_files']:,}")
        table.add_row("Remaining", f"{summary['remaining_records']:,}")
        
        # Calculate estimated completion
        if summary['extracted_count'] > 0 and summary['remaining_records'] > 0:
            # Assuming 50 records per weekday
            days_remaining = summary['remaining_records'] / 50
            weeks_remaining = days_remaining / 5  # 5 weekdays per week
            table.add_row("Est. Completion", f"~{weeks_remaining:.1f} weeks")
        
        console.print(table)
        
        # Show file sizes
        detailed_dir = Path("data/detailed")
        if detailed_dir.exists():
            total_size = sum(f.stat().st_size for f in detailed_dir.glob("*.json"))
            avg_size = total_size / summary['actual_files'] if summary['actual_files'] > 0 else 0
            
            console.print(f"\n📁 Storage Information:")
            console.print(f"  Total Size: {total_size / (1024*1024):.1f} MB")
            console.print(f"  Average File Size: {avg_size / 1024:.1f} KB")
            
            # Estimate final size
            if summary['total_records'] > 0:
                estimated_total = (avg_size * summary['total_records']) / (1024*1024)
                console.print(f"  Estimated Final Size: {estimated_total:.1f} MB")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()