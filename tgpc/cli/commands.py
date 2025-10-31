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
        
        saved_path = engine.save_records(records, output)
        console.print(f"Extracted {len(records):,} records to {saved_path}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option("--dataset", "-d", default="pharmacists.json", help="Dataset file to use")
@click.option("--start-index", "-s", default=0, help="Start index for extraction")
@click.option("--batch-size", "-b", default=100, help="Batch size for processing")
@click.pass_context
def detailed(ctx, dataset, start_index, batch_size):
    """Extract detailed pharmacist information."""
    try:
        config = Config.load(config_file=ctx.obj.get("config_file"))
        engine = TGPCEngine(config)
        
        # Load basic records
        basic_records = engine.load_records(dataset)
        reg_numbers = [record.registration_number for record in basic_records]
        
        console.print(f"Extracting detailed info for {len(reg_numbers)} records...")
        detailed_records = engine.extract_detailed_records(
            reg_numbers,
            start_index=start_index,
            batch_size=batch_size
        )
        
        output_file = f"detailed_{dataset}"
        saved_path = engine.save_records(detailed_records, output_file)
        console.print(f"Extracted {len(detailed_records):,} detailed records to {saved_path}")
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


if __name__ == "__main__":
    main()