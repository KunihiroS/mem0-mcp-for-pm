# mem0 MCP Server for Project Management

**Version: 0.2.0**

mem0 MCP Server acts as a bridge between MCP Host applications and the mem0 cloud service, providing advanced project management memory capabilities for MCP Host AI.

This fork is focused on project management use cases, supporting structured project data, semantic search, and robust integration with the mem0 API.

Key features:
- Project memory storage and retrieval
- Semantic search for relevant project information
- Structured project management data handling
- Fully tested stdio MCP Server tools
- Flexible logging: default to stderr, file output with `--logfile`

## Installation

### Requirements

- Python 3.12 or newer
- mem0 API key (set as environment variable MEM0_API_KEY)
- (Optional) mcp-proxy for Cline/Roo integration

### pipx (recommended)
```bash
pipx install .
```
To upgrade:
```bash
pipx uninstall mem0-mcp-for-pm
pipx install .
```

### uv/venv (alternative)
```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e .
```

## Usage

Start the MCP Server (stdio mode):
```bash
mem0-mcp-for-pm
```

Send a JSON request via stdin:
```bash
echo '{"tool": "get_all_project_memories", "arguments": {}}' | mem0-mcp-for-pm
```

To enable file logging:
```bash
echo '{"tool": "get_all_project_memories", "arguments": {}}' | mem0-mcp-for-pm --logfile /tmp/mem0.log
```
(Default: logs to stderr only. No log file is created unless --logfile is specified.)

## Available Tools

- add_project_memory: Add new project management information
- get_all_project_memories: Retrieve all stored project information
- search_project_memories: Search for specific project information
- update_project_memory: Update existing project information
- delete_project_memory: Delete a specific project memory
- delete_all_project_memories: Delete multiple project memories by filter

All tools are fully tested and work in stdio MCP Server mode.

## Logging

- By default, logs are output to stderr only.
- To output logs to a file, use the `--logfile` command-line argument.
- No `.log` file is created unless explicitly specified.

## License

See LICENSE file for details.