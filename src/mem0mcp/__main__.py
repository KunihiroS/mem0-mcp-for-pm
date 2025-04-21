"""
mem0 MCP for Project Management - Module Entry Point

This module provides the entry point when executed as 'python -m mem0mcp'.
"""

import asyncio
from .server import main as _main

def main():
    asyncio.run(_main())

if __name__ == "__main__":
    # Entry point when executed as 'python -m mem0mcp'
    main()
