import logging
import json
from typing import Dict, Any, List, Union
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions
import mcp.types as types
from mem0 import MemoryClient
import os
from pathlib import Path
import sys
import asyncio

logger = logging.getLogger("mem0-mcp-server")
logger.setLevel(logging.DEBUG)
logger.handlers.clear()
logger.propagate = False

def setup_logging(log: str, logfile: str):
    if log == "on":
        if not logfile or not logfile.startswith("/"):
            print("[FATAL] --logfile must be an absolute path when --log=on", file=sys.stderr)
            sys.exit(1)
        log_dir = os.path.dirname(logfile)
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except Exception as e:
                print(f"[FATAL] Failed to create log directory: {log_dir} error={e}", file=sys.stderr)
                sys.exit(1)
        try:
            file_handler = logging.FileHandler(logfile, mode="a", encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            # --- Also add FileHandler to the root logger to capture all logs ---
            root_logger = logging.getLogger()
            root_logger.handlers.clear()
            root_logger.setLevel(logging.DEBUG)
            root_logger.addHandler(file_handler)
            logger.debug(f"=== MCP Server log initialized: {logfile} ===")
        except Exception as e:
            print(f"[FATAL] Failed to create log file: {logfile} error={e}", file=sys.stderr)
            sys.exit(1)
    elif log == "off":
        # Completely disable logging functionality
        logging.disable(logging.CRITICAL)
    else:
        print("[FATAL] --log must be 'on' or 'off'", file=sys.stderr)
        sys.exit(1)

settings = {
    "APP_NAME": "mem0-mcp-for-pm",
    "APP_VERSION": "0.3.0"
}

server = Server(settings["APP_NAME"])
mem0_client = MemoryClient()
DEFAULT_USER_ID = "cursor_mcp"
CUSTOM_INSTRUCTIONS = """
Interpret and Extract **Project Management Information** from input:

# Overview
- The input assumed to be a string in TOML format, but may not be.
- The important job is to extract all key-value pairs and make them entries as memories.

# Robustness Guidelines
- If the input is not valid TOML, attempt to extract as many structured key-value pairs as possible.
- If required fields are missing, infer or synthesize them from context if possible.
- In case of ambiguous or unstructured input, extract and record as much relevant information as possible, even as plain text.
- Normalize all dates, times, and numbers to standard formats (e.g., ISO 8601 for dates).
- When possible, align field names and structures to the provided templates for consistency.

# Security and Privacy (if applicable)
- If personal or sensitive information is detected, tag the relevant fields clearly (e.g., "PII": true).

# Primary Extraction Categories
- Project Status: Extract current progress state, completion levels, and overall status.
- Task Management: Identify tasks with their priorities, dependencies, statuses, and deadlines.
- Decision Records: Document decisions, their rationale, implications, and related constraints.
- Resource Allocation: Capture information about resource usage, assignments, and availability.
- Risk Assessment: Identify potential risks, their impact ratings, and mitigation strategies.
- Technical Artifacts: Extract technical specifications, dependencies, and implementation notes.

# Memory Structure and Templates
- The following templates are expected:
  - Project Status: Track overall project progress and current focus. Mandatory Fields: `name`, `purpose`. Optional Fields: `version`, `phase`, `completionLevel`, `milestones`, `currentFocus`.
  - Task Management: Manage task priorities, statuses, and dependencies. Mandatory Fields: `description`, `status`. Optional Fields: `deadline`, `assignee`, `dependencies`.
  - Decision Records: Document decisions, their rationale, implications, and constraints. Mandatory Fields: `topic`, `selected`, `rationale`. Optional Fields: `options`, `implications`, `constraints`, `responsible`, `stakeholders`.
  - Resource Allocation: Capture information about resource usage, assignments, and availability. Mandatory Fields: None. Optional Fields: `team`, `infrastructure`, `budget`.
  - Risk Assessment: Identify potential risks, their impact ratings, and mitigation strategies. Mandatory Fields: `description`, `impact`, `probability`. Optional Fields: `mitigation`, `owner`, `monitoringItems`.
  - Technical Artifacts: Extract technical specifications, dependencies, and implementation notes. Mandatory Fields: None. Optional Fields: `architecture`, `technologies`, `standards`.
- Refer to the 'Memory Structure and Templates' section in the documentation for detailed descriptions and examples.

# Metadata Extraction (when available)
- Temporal Context: Extract timestamps, durations, deadlines, and sequence information.  Format dates and times using ISO 8601 format.
- Project Context: Identify project names, phases, domains, and scope indicators.
- Relationship Mapping: Extract relationships between extracted elements, such as:
  - 'relatedTo': Elements that are related to each other (bidirectional).
  - 'enables': Element A enables element B (directional).
  - 'blockedBy': Element A is blocked by element B (directional).
  - 'dependsOn': Element A depends on element B (directional).
  - Relationships should be extracted as strings or arrays of strings.

# Interpretation Guidelines
- For structured input (expected TOML): Preserve the structural hierarchy while enriching with contextual metadata, and extract key-value pairs.
- For code-structured representations: Analyze both the structural patterns (e.g., variable names, function names, class names) and the semantic content (e.g., comments, descriptions, code logic).
- For mixed-format input: Prioritize semantic content while acknowledging structural hints (e.g., headings, lists, tables). Extract information from text, code snippets, and structured data blocks.

# Output Structure Formation
- Extracted information should be categorized according to the Primary Extraction Categories.
- Preserve original identifiers and reference keys (e.g., project name, task ID) for continuity.
- When metadata such as project name and timestamp are not explicitly provided as top-level keys, attempt to infer them from the context (e.g., from comments).
"""
mem0_client.update_project(custom_instructions=CUSTOM_INSTRUCTIONS)

# Tool Definitions
add_project_memory_tool = types.Tool(
    name="add_project_memory",
    description="""
    Add new project management information to mem0.

    This tool is designed to store structured project information including:
    - Project Status
    - Task Management
    - Decision Records
    - Resource Allocation
    - Risk Assessment
    - Technical Artifacts

    Information must be formatted according to the templates defined in Memory Structure and Templates,
    using the **TOML** data format, and must include project name and timestamp as metadata.

    Args:
        messages: A list of message objects containing the project information.
            The content within the messages should ideally be TOML formatted.
            - Use the provided category templates as a basis.
            - Include all relevant fields and metadata (e.g., project name, timestamp) as TOML keys.
        run_id: (Optional) Session identifier for organizing related memories into logical groups.

            Recommended format: "project:name:category:subcategory"
            Example: "project:member-webpage:sprint:2025-q2-sprint3"
        metadata: (Optional) Additional structured information about this memory.
            Recommended TOML table:
            [metadata]
            type = "meeting|task|decision|status|risk"
            priority = "high|medium|low"
            tags = ["tag1", "tag2"]
        immutable: (Optional) If true, prevents future modifications to this memory.
        expiration_date: (Optional) Date when this memory should expire (YYYY-MM-DD).
        custom_categories: (Optional) Custom categories for organizing project information.
        includes: (Optional) Specific aspects or preferences to include in the memory.
        excludes: (Optional) Specific aspects or preferences to exclude from the memory.
        infer: (Optional) Controls whether to process and infer structure from the input.

    Example:
        ```toml
        # Project Status Example
        category = "Project Status"
        project = "project-name"
        timestamp = "2025-03-23T10:58:29+09:00"
        name = "Project Name"
        purpose = "Brief description"
        version = "1.2.0"
        phase = "development"
        completionLevel = 0.65
        milestones = ["Planning", "Development"]
        currentFocus = ["Feature X", "Component Y"]

        [metadata]
        type = "status"
        priority = "high"
        tags = ["frontend", "backend"]
        ```

    Returns:
        str: A success message if the project information was added successfully, or an error message if there was an issue.
    """,
    inputSchema={
        "type": "object",
        "properties": {

            "messages": {
                "type": "array",
                "description": "A list of message objects (e.g., [{'role': 'user', 'content': 'TOML content...'}]).",
                "items": {
                    "type": "object",
                    "properties": {
                        "role": {"type": "string"},
                        "content": {"type": "string"}
                    },
                    "required": ["role", "content"]
                }
            },
            "run_id": {
                "type": "string",
                "description": "Session identifier to group related memories. Use the same value for add/search. Recommended format: 'project:name:category:subcategory' (e.g., 'project:member-webpage:sprint:2025-q2-sprint3')."
            },
            "metadata": {
                "type": "object",
                "description": "Additional structured metadata for filtering/search. Recommended TOML table: [metadata] type='task' priority='high' tags=['backend']."
            },
            "immutable": {
                "type": "boolean",
                "description": "If true, prevents future updates to this memory."
            },
            "expiration_date": {
                "type": "string",
                "description": "Expiration date for this memory (YYYY-MM-DD, ISO 8601). After this date, the memory may be deleted automatically."
            },
            "custom_categories": {
                "type": "object",
                "description": "Custom categories for organizing project information. Example: {'category': 'release', 'phase': 'beta'}. Optional."
            },
            "includes": {
                "type": "string",
                "description": "Specific aspects or preferences to include in memory extraction. Optional."
            },
            "excludes": {
                "type": "string",
                "description": "Specific aspects or preferences to exclude from memory extraction. Optional."
            },
            "infer": {
                "type": "boolean",
                "description": "If true, enables automatic structure inference from the input. Optional."
            }
        },
        "required": ["messages"]
    }
)

get_all_project_memories_tool = types.Tool(
    name="get_all_project_memories",
    description="""
    Retrieve a list of project memories stored in mem0.

    This tool allows you to search and filter project memories by category, project name, creation date, tags, and other metadata.
    Use filters to narrow down results (e.g., by project, type, date range).
    Supports pagination for large result sets.

    Args:
        page: (Optional) The page number to retrieve (1-based index). Default is 1.
        page_size: (Optional) The number of items per page. Default is 50. Maximum is 100.
        filters: (Optional) Dictionary of filters to apply. Example:
            {
                "category": "Task Management",
                "project": "ProjectA",
                "created_at__gte": "2025-04-01",
                "tags__contains": "backend"
            }
            - Supported filter keys: category, project, created_at (with __gte, __lte), tags, owner, etc.
            - Use "__gte" for "greater than or equal", "__lte" for "less than or equal".

    Returns:
        list or dict: If successful, returns a list of memory objects or a paginated dict as described.
    """,
    inputSchema={
        "type": "object",
        "properties": {
            "page": {
                "type": "integer",
                "description": "The page number to retrieve (1-based). Default is 1."
            },
            "page_size": {
                "type": "integer",
                "description": "The number of items per page. Default is 50. Maximum is 100."
            },
            "filters": {
                "type": "object",
                "description": "Filter criteria as a dictionary. Example: {\"category\": \"Task Management\", \"project\": \"ProjectA\", \"created_at__gte\": \"2025-04-01\"}. Supported keys: category, project, created_at__gte, created_at__lte, tags, owner, etc."
            }
        }
    }
)

search_project_memories_tool = types.Tool(
    name="search_project_memories",
    description="""
Search through stored project management information using semantic search (v2 API).

This tool uses the v2 search API, which supports advanced filtering capabilities.

Args:
    query: The search query string.
    page: (Optional) The page number to retrieve (1-based index). Default is 1.
    page_size: (Optional) The number of items per page. Default is 50. Maximum is 100.
    filters: (Optional) Dictionary of filters to apply. Example:
        {
            "category": "Task Management",
            "project": "ProjectA",
            "created_at__gte": "2025-04-01",
            "tags__contains": "backend"
        }
        - Supported filter keys: category, project, created_at (with __gte, __lte), tags, owner, etc.
        - Use "__gte" for "greater than or equal", "__lte" for "less than or equal".

Returns:
    list: List of memory objects with structure:
    {
        "id": "memory-id-for-deletion-operations",
        "memory": "actual memory content",
        "user_id": "user identifier",
        "metadata": {},
        "categories": [],
        "immutable": false,
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
""",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query string."},
            "page": {"type": "integer", "description": "The page number to retrieve (1-based). Default is 1."},
            "page_size": {"type": "integer", "description": "The number of items per page. Default is 50. Maximum is 100."},
            "filters": {"type": "object", "description": "Optional filters to apply to the search."}
        },
        "required": ["query"]
    }
)

update_project_memory_tool = types.Tool(
    name="update_project_memory",
    description="""
Update an existing project memory with new content.

This tool updates a memory identified by its ID. Use this when making minor changes or corrections, and when you need to preserve the memory's ID and creation timestamp.

- The `data` argument must be a TOML-formatted string, using the same templates as add_project_memory.
- Always include project name and timestamp in the TOML content.
- Use update for minor edits; for major restructuring, consider delete+create.

Args:
    memory_id: The unique identifier of the memory to update (as returned by get/search).
    data: The new content for the memory, in TOML format. Must include project name and timestamp.

Returns:
    dict: The updated memory object with complete metadata.

Example usage:
    memory_id = "abc123"
    data = '''
    category = "Task Management"
    project = "project-name"
    timestamp = "2025-04-29T15:54:00+09:00"
    description = "Update API endpoint"
    status = "completed"
    [metadata]
    type = "task"
    priority = "medium"
    tags = ["backend"]
    '''
""",
    inputSchema={
        "type": "object",
        "properties": {
            "memory_id": {
                "type": "string",
                "description": "The unique identifier of the memory to update. Obtainable via get/search."
            },
            "data": {
                "type": "string",
                "description": "The new content for the memory, as a TOML-formatted string. Use the recommended templates. Must include project name and timestamp."
            }
        },
        "required": ["memory_id", "data"]
    }
)

delete_project_memory_tool = types.Tool(
    name="delete_project_memory",
    description="""
Delete a specific project memory from mem0.

This tool removes a memory by its ID. Use this when you want to permanently remove a memory entry. Deletion is irreversible.

Args:
    memory_id: The unique identifier of the memory to delete. Obtainable via get/search.

Returns:
    str: A success message if the memory was deleted successfully, or an error message if there was an issue.
""",
    inputSchema={
        "type": "object",
        "properties": {
            "memory_id": {
                "type": "string",
                "description": "The unique identifier of the memory to delete. Obtainable via get/search."
            }
        },
        "required": ["memory_id"]
    }
)

delete_all_project_memories_tool = types.Tool(
    name="delete_all_project_memories",
    description="Delete multiple project memories based on specified filters. This tool uses the delete_all method to remove multiple memories based on filter criteria. IMPORTANT: Use this tool with caution as it will delete ALL memories that match the specified filters. If no filters are specified, it could potentially delete ALL memories. Args: user_id (str, optional): Filter memories by user ID. agent_id (str, optional): Filter memories by agent ID. app_id (str, optional): Filter memories by app ID. run_id (str, optional): Filter memories by run ID. metadata (dict, optional): Filter memories by metadata. org_id (str, optional): Filter memories by organization ID. project_id (str, optional): Filter memories by project ID. Returns: str: A success message if the memories were deleted successfully, or an error message if there was an issue.",
    inputSchema={
        "type": "object",
        "properties": {
"user_id": {"type": "string", "description": "Filter memories by user ID."},
"agent_id": {"type": "string", "description": "Filter memories by agent ID."},
"app_id": {"type": "string", "description": "Filter memories by app ID."},
"run_id": {"type": "string", "description": "Filter memories by run ID."},
"metadata": {"type": "object", "description": "Filter memories by metadata."},
"org_id": {"type": "string", "description": "Filter memories by organization ID."},
"project_id": {"type": "string", "description": "Filter memories by project ID."}
        }
    }
)

# --- Add global exception hook ---
def log_unhandled_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = log_unhandled_exception
# --- End of global exception hook ---

# --- Add asyncio event loop exception handler ---
def handle_asyncio_exception(loop, context):
    logger.critical(f"Asyncio unhandled exception: {context.get('message')}", exc_info=context.get('exception'))

try:
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_asyncio_exception)
except Exception as e:
    logger.error(f"Failed to set asyncio exception handler: {e}")
# --- End of asyncio event loop exception handler ---

@server.list_tools()
async def list_tools() -> List[types.Tool]:
    return [
        add_project_memory_tool,
        get_all_project_memories_tool,
        search_project_memories_tool,
        update_project_memory_tool,
        delete_project_memory_tool,
        delete_all_project_memories_tool
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    # Log tool invocation
    logger.info(f"Tool invoked: name={name}, args={arguments}")
    # Flush logs immediately
    for h in logger.handlers:
        try:
            h.flush()
        except Exception:
            pass
    try:
        if name == "add_project_memory":
            api_params = {
                "messages": arguments["messages"],
                "user_id": DEFAULT_USER_ID,
                "output_format": "v1.1",
                "version": "v2"
            }
            for key in [
                "run_id", "metadata", "immutable", "expiration_date",
                "custom_categories", "includes", "excludes", "infer"
            ]:
                if key in arguments:
                    api_params[key] = arguments[key]
            logger.debug(f"Calling mem0_client.add with params: {api_params}")
            mem0_client.add(**api_params)
            return [types.TextContent(type="text", text="Successfully added project memory")]

        elif name == "get_all_project_memories":
            params = {k: v for k, v in arguments.items() if v is not None}
            # Add default user_id if no filter is specified
            if not any(k in params for k in ["run_id", "user_id", "agent_id", "app_id"]):
                params["user_id"] = DEFAULT_USER_ID
            result = mem0_client.get_all(**params)
            return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

        elif name == "search_project_memories":
            params = {k: v for k, v in arguments.items() if v is not None}
            # Wrap filters for get_all_project_memories_tool
            if "filters" not in params and any(k in params for k in ["category", "project", "created_at__gte", "created_at__lte", "tags", "owner"]):
                # If simple filters are specified, wrap them in filters
                filter_keys = ["category", "project", "created_at__gte", "created_at__lte", "tags", "owner"]
                params["filters"] = {k: params.pop(k) for k in filter_keys if k in params}
            # Add default user_id
            if not any(k in params for k in ["run_id", "user_id", "agent_id", "app_id"]):
                params["user_id"] = DEFAULT_USER_ID
            result = mem0_client.search(**params)
            return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

        elif name == "update_project_memory":
            params = {k: v for k, v in arguments.items() if v is not None}
            # Convert text to data according to mem0 official specification
            if "text" in params:
                params["data"] = params.pop("text")
            mem0_client.update(**params)
            return [types.TextContent(type="text", text="Successfully updated project memory")]

        elif name == "delete_project_memory":
            params = {k: v for k, v in arguments.items() if v is not None}
            mem0_client.delete(**params)
            return [types.TextContent(type="text", text="Successfully deleted project memory")]

        elif name == "delete_all_project_memories":
            filter_params = {k: v for k, v in arguments.items() if v is not None}
            mem0_client.delete_all(**filter_params)
            return [types.TextContent(type="text", text="Successfully deleted matching memories")]

        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

        logger.info(f"Tool finished: name={name}")
    except Exception as e:
        logger.exception(f"Tool error: name={name}, args={arguments}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def main(log: str = None, logfile: str = None):
    setup_logging(log, logfile)
    try:
        async with stdio_server() as streams:
            await server.run(
                streams[0],
                streams[1],
                InitializationOptions(
                    server_name=settings["APP_NAME"],
                    server_version=settings["APP_VERSION"],
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(resources_changed=True),
                        experimental_capabilities={},
                    ),
                ),
            )
    except Exception:
        logger.exception("Fatal error in server.run", exc_info=True)
        raise
