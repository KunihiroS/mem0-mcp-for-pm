"""
mem0 MCP for Project Management - Main Package

This package provides a server to integrate the mem0 service with an MCP Host.
It implements features for storing, searching, and updating project management information.
"""

import sys
from .server import main as server_main

def main():
    """
    Entry point function - used when executed via pipx/uvx
    """
    return server_main()