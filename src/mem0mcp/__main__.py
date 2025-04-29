"""
mem0 MCP for Project Management - Module Entry Point

This module provides the entry point when executed as 'python -m mem0mcp'.
"""

import argparse
import sys
import asyncio
from .server import main as _main

def parse_args():
    parser = argparse.ArgumentParser(description="mem0 MCP Server")
    parser.add_argument("--log", required=True, choices=["on", "off"], help="Enable or disable logging. Must be 'on' or 'off'.")
    parser.add_argument("--logfile", required=False, help="Absolute path for log file (required if --log=on)")
    args = parser.parse_args()

    # Validation
    if args.log == "on":
        if not args.logfile:
            parser.error("--logfile is required when --log=on")
        if not args.logfile.startswith("/"):
            parser.error("--logfile must be an absolute path")
    elif args.log == "off":
        if args.logfile:
            parser.error("--logfile must not be specified when --log=off")
    return args

def main():
    args = parse_args()
    asyncio.run(_main(log=args.log, logfile=args.logfile))

if __name__ == "__main__":
    # Entry point when executed as 'python -m mem0mcp'
    main()
