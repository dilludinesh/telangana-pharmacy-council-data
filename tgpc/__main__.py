"""
CLI entry point for TGPC system.
"""

import sys
import argparse
from tgpc.manager import Manager

def main():
    parser = argparse.ArgumentParser(description="TGPC Rx Registry Manager")
    parser.add_argument("command", choices=["update", "sync"], help="Command to execute")
    args = parser.parse_args()

    manager = Manager()

    if args.command == "update":
        manager.run_daily_update()
    elif args.command == "sync":
        manager.sync_to_supabase()

if __name__ == "__main__":
    main()
