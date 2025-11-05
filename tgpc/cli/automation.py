"""
CLI commands for TGPC automation management.
"""

import click
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from tgpc.automation.scheduler import get_scheduler, start_daily_automation, stop_daily_automation
from tgpc.automation.daily_updater import run_daily_update

console = Console()


@click.group()
def automation():
    """Manage TGPC automation and scheduling."""
    pass


@automation.command()
@click.option("--time", "-t", default="02:00", help="Daily update time (HH:MM format)")
def start(time):
    """Start daily automation scheduler."""
    try:
        start_daily_automation(time)
        console.print(f"[green]✅ Daily automation started at {time}[/green]")
        console.print("The system will automatically update rx.json daily with:")
        console.print("• Data integrity validation")
        console.print("• Duplicate detection and removal")
        console.print("• Secure backups with checksums")
        console.print("• Safety checks and rollback protection")
    except Exception as e:
        console.print(f"[red]❌ Failed to start automation: {e}[/red]")


@automation.command()
def stop():
    """Stop daily automation scheduler."""
    try:
        stop_daily_automation()
        console.print("[yellow]⏹️ Daily automation stopped[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Failed to stop automation: {e}[/red]")


@automation.command()
def status():
    """Show automation status."""
    try:
        scheduler = get_scheduler()
        status = scheduler.get_status()
        
        # Create status table
        table = Table(title="TGPC Automation Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        # Basic status
        table.add_row("Running", "✅ Yes" if status["is_running"] else "❌ No")
        table.add_row("Update Time", status["update_time"] or "Not set")
        table.add_row("Next Scheduled", status["next_scheduled"] or "Not scheduled")
        
        # Last update info
        if status["last_update"]:
            table.add_row("Last Update", status["last_update"])
            
            if status["last_result"]:
                result = status["last_result"]
                success_icon = "✅" if result["success"] else "❌"
                table.add_row("Last Result", f"{success_icon} {'Success' if result['success'] else 'Failed'}")
                table.add_row("Total Records", f"{result['total_records']:,}")
                table.add_row("New Records", str(result["new_records"]))
                
                if result["errors"]:
                    table.add_row("Errors", str(len(result["errors"])))
        else:
            table.add_row("Last Update", "Never")
        
        console.print(table)
        
        # Show errors if any
        if status["last_result"] and status["last_result"]["errors"]:
            error_panel = Panel(
                "\n".join(status["last_result"]["errors"][:3]),
                title="Recent Errors",
                border_style="red"
            )
            console.print(error_panel)
            
    except Exception as e:
        console.print(f"[red]❌ Failed to get status: {e}[/red]")


@automation.command()
def update():
    """Run manual update now."""
    try:
        console.print("[blue]🔄 Running manual update...[/blue]")
        
        result = run_daily_update()
        
        if result.success:
            console.print(f"[green]✅ Update successful![/green]")
            
            # Create results table
            table = Table(title="Update Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="white")
            
            table.add_row("Total Records", f"{result.total_records:,}")
            table.add_row("New Records", str(result.new_records))
            table.add_row("Removed Records", str(result.removed_records))
            table.add_row("Duplicates Removed", str(result.duplicates_removed))
            table.add_row("Data Integrity", f"{result.data_integrity_score:.3f}")
            table.add_row("Backup Created", "✅ Yes" if result.backup_created else "❌ No")
            
            console.print(table)
            
            if result.warnings:
                warning_panel = Panel(
                    "\n".join(result.warnings),
                    title="Warnings",
                    border_style="yellow"
                )
                console.print(warning_panel)
                
        else:
            console.print(f"[red]❌ Update failed![/red]")
            
            if result.errors:
                error_panel = Panel(
                    "\n".join(result.errors),
                    title="Errors",
                    border_style="red"
                )
                console.print(error_panel)
                
    except Exception as e:
        console.print(f"[red]❌ Manual update failed: {e}[/red]")


@automation.command()
def validate():
    """Validate current data integrity."""
    try:
        from tgpc.core.engine import TGPCEngine
        from tgpc.automation.daily_updater import DataIntegrityValidator
        
        console.print("[blue]🔍 Validating current data...[/blue]")
        
        engine = TGPCEngine()
        validator = DataIntegrityValidator()
        
        # Load current data
        records = engine.load_records("rx.json")
        
        # Validate
        clean_records, validation_report = validator.validate_records(records)
        consistency_report = validator.verify_data_consistency(clean_records)
        
        # Display results
        table = Table(title="Data Validation Results")
        table.add_column("Check", style="cyan")
        table.add_column("Result", style="white")
        
        table.add_row("Total Records", f"{validation_report['total_input_records']:,}")
        table.add_row("Clean Records", f"{validation_report['clean_records']:,}")
        table.add_row("Duplicates Found", str(validation_report['duplicates_found']))
        table.add_row("Invalid Records", str(validation_report['invalid_records']))
        table.add_row("Integrity Score", f"{validation_report['integrity_score']:.3f}")
        table.add_row("Data Quality Score", f"{consistency_report['data_quality_score']:.3f}")
        
        console.print(table)
        
        # Show issues if any
        if validation_report['integrity_issues']:
            issue_panel = Panel(
                "\n".join(validation_report['integrity_issues'][:5]),
                title="Data Issues",
                border_style="yellow"
            )
            console.print(issue_panel)
            
    except Exception as e:
        console.print(f"[red]❌ Validation failed: {e}[/red]")


if __name__ == "__main__":
    automation()