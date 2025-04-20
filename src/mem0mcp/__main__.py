"""
mem0 MCP for Project Management - Module Entry Point

This module provides the entry point when executed as 'python -m mem0mcp'.
"""

from .server import main as server_main

if __name__ == "__main__":
    # Entry point when executed as 'python -m mem0mcp'
    exit(server_main())