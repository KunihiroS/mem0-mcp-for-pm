#!/usr/bin/env python3
"""
Simple MCP main entry point.
This module implements a basic stdio-based MCP server.
"""

import sys
import json
import logging
from typing import Dict, Any


def process_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process an incoming MCP request.
    Just a stub that echoes the request back with a hello message.
    """
    return {
        "status": "success",
        "message": "Hello from MCP Threads Server!",
        "received": request
    }


def main() -> None:
    """Main entry point for the MCP server."""
    # Configure logging to file
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='mcp-threads.log'
    )
    
    logging.info("MCP Threads server started")
    
    # Print a startup message to stderr (will be visible during manual testing)
    print("MCP Threads server is running. Send JSON requests via stdin.", file=sys.stderr)
    
    # Process JSON requests from stdin
    for line in sys.stdin:
        try:
            # Parse the incoming JSON request
            request = json.loads(line)
            logging.info(f"Received request: {request}")
            
            # Process the request
            response = process_request(request)
            
            # Send the response as JSON to stdout
            print(json.dumps(response), flush=True)
            logging.info(f"Sent response: {response}")
            
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON received: {e}")
            error_response = {
                "status": "error",
                "error": "Invalid JSON",
                "details": str(e)
            }
            print(json.dumps(error_response), flush=True)
            
        except Exception as e:
            logging.error(f"Error processing request: {e}")
            error_response = {
                "status": "error",
                "error": "Internal server error",
                "details": str(e)
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()