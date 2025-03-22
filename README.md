# mem0 MCP Server

mem0 MCP Server is a bridge between MCP Host applications and the mem0 cloud service, providing project management memory capabilities.

## Features

- Project memory storage and retrieval
- Semantic search for finding relevant project information
- Structured project management data handling

## Installation

```bash
pip install -r requirements.txt

Usage
python main.py --host 0.0.0.0 --port 8080

Available Tools
add_project_memory: Add new project management information
get_all_project_memories: Retrieve all stored project information
search_project_memories: Search for specific project information