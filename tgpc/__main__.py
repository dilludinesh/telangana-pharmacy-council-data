"""
CLI entry point for TGPC system.
"""

import sys
import argparse
from tgpc.manager import Manager

def main():
    parser = argparse.ArgumentParser(description="TGPC Rx Registry Manager")
    subparsers = parser.add_subparsers(dest='command', help='Available commands', required=True)

    # Update command
    update_parser = subparsers.add_parser('update', help='Run daily update process')

    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync data to Supabase')

    args = parser.parse_args()
    
    manager = Manager()

    if args.command == 'update':
        manager.run_daily_update()
    elif args.command == 'sync':
        manager.sync_to_supabase()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
