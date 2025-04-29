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

# ワークスペースルートを正しく指定
project_root = Path(__file__).parent.parent.parent.resolve()
os.makedirs(project_root, exist_ok=True)
log_path = project_root / ".mcp_server.log"

print(f"[MCP DEBUG] __file__={__file__}")
print(f"[MCP DEBUG] log_path={log_path}")
print(f"[MCP DEBUG] cwd={os.getcwd()}")

try:
    file_handler = logging.FileHandler(str(log_path), mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    # --- ルートロガーにも FileHandler を追加して全ログを捕捉 ---
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    logger.debug("=== MCP Server ログ初期化: DEBUGレベル ===")
except Exception as e:
    print(f"ログファイル作成失敗: {log_path} error={e}")

settings = {
    "APP_NAME": "mem0-mcp-for-pm",
    "APP_VERSION": "0.2.4"
}

server = Server(settings["APP_NAME"])
mem0_client = MemoryClient()
DEFAULT_USER_ID = "cursor_mcp"
CUSTOM_INSTRUCTIONS = """
Interpret and Extract Project Management Information:

# Primary Extraction Categories
- Project Status: Extract current progress state, completion levels, and overall status.
- Task Management: Identify tasks with their priorities, dependencies, statuses, and deadlines.
- Decision Records: Document decisions, their rationale, implications, and related constraints.
- Resource Allocation: Capture information about resource usage, assignments, and availability.
- Risk Assessment: Identify potential risks, their impact ratings, and mitigation strategies.
- Technical Artifacts: Extract technical specifications, dependencies, and implementation notes.

# Memory Structure and Templates
- Use the following templates to structure your input:
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
- For structured input (JavaScript/JSON objects): Preserve the structural hierarchy while enriching with contextual metadata, and extract key-value pairs.
- For code-structured representations: Analyze both the structural patterns (e.g., variable names, function names, class names) and the semantic content (e.g., comments, descriptions, code logic).
- For mixed-format input: Prioritize semantic content while acknowledging structural hints (e.g., headings, lists, tables). Extract information from text, code snippets, and structured data blocks.

# Output Structure Formation
- Extracted information should be categorized according to the Primary Extraction Categories.
- Preserve original identifiers and reference keys (e.g., project name, task ID) for continuity.
- When metadata such as project name and timestamp are not explicitly provided as top-level keys, attempt to infer them from the context (e.g., from comments).
- The output should be a JSON object with the following structure:
  {
    "category": "string",  // Primary Extraction Category (e.g., "Task Management")
    "content": "any",      // Extracted content (e.g., task details)
    "metadata": "object",  // Extracted metadata (e.g., {"project": "ProjectA", "deadline": "2023-12-01"})
    "relationships": "array"  // Extracted relationships (e.g., [{"type": "dependsOn", "target": "TaskB"}])
  }
  // Note: The current implementation of get_all_project_memories and search_project_memories returns a
  // flattened list of strings. This output structure is a future goal and may require changes to those tools.
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

    Information should be formatted according to the templates defined in Memory Structure and Templates,
    using structured data formats (JavaScript objects, JSON, YAML), and include project name and timestamp as metadata.

    Args:
        text: The project information to add to mem0.
        run_id: (Optional) Session identifier for organizing related memories into logical groups.
            Recommended format: "project:name:category:subcategory"
            Example: "project:member-webpage:sprint:2025-q2-sprint3"
        metadata: (Optional) Additional structured information about this memory.
                Recommended schema: {"type": "meeting|task|decision|status|risk", 
                                    "priority": "high|medium|low",
                                    "tags": ["tag1", "tag2"]}
        immutable: (Optional) If True, prevents future modifications to this memory.
        expiration_date: (Optional) Date when this memory should expire (YYYY-MM-DD).
        custom_categories: (Optional) Custom categories for organizing project information.
        includes: (Optional) Specific aspects or preferences to include in the memory.
        excludes: (Optional) Specific aspects or preferences to exclude from the memory.
        infer: (Optional) Controls whether to process and infer structure from the input.

    Example:
        ```javascript
        // [PROJECT: project-name] [TIMESTAMP: 2025-03-23T10:58:29+09:00]
        const projectStatus = {
          project: "project-name",
          timestamp: "2025-03-23T10:58:29+09:00",
          overview: {
            name: "Project Name",
            purpose: "Brief description"
          },
          // ...
        };
        ```

    Returns:
        str: A success message if the project information was added successfully, or an error message if there was an issue.
    """,
    inputSchema={
        "type": "object",
        "properties": {
            "text": {"type": "string"},
"run_id": {"type": "string", "description": "Session identifier (e.g., project:foo:status:2025-q2)"},
"metadata": {"type": "object", "description": "Metadata to improve searchability (e.g., type, priority, tags)"},
"immutable": {"type": "boolean", "description": "If True, prevents future updates"},
"expiration_date": {"type": "string", "description": "Expiration date for this memory (YYYY-MM-DD)"},
"custom_categories": {"type": "object", "description": "Custom categories (optional)"},
"includes": {"type": "string", "description": "Aspects to include in memory extraction (optional)"},
"excludes": {"type": "string", "description": "Aspects to exclude from memory extraction (optional)"},
"infer": {"type": "boolean", "description": "Whether to enable structure inference (optional)"}
        },
        "required": ["text"]
    }
)

get_all_project_memories_tool = types.Tool(
    name="get_all_project_memories",
    description="""
Retrieve all stored project management information for the default user (v2 API).

This tool uses the v2 get_all API, which supports pagination and filtering.

Args:
    page: (Optional) The page number to retrieve. Default is 1.
    page_size: (Optional) The number of items per page. Default is 50.
    filters: (Optional) A dictionary of filters to apply.

Returns:
    list or dict: If successful, returns a list of memory objects with structure:
    {
        "id": "memory-id-for-deletion-operations",
        "name": "memory name",
        "owner": "user identifier",
        "metadata": {},
        "immutable": false,
        "created_at": "timestamp",
        "updated_at": "timestamp",
        "organization": "organization identifier"
    }
    In case of pagination, returns:
    {
        "count": total_count,
        "next": "URL for next page or null",
        "previous": "URL for previous page or null",
        "results": [list of memory objects as described above]
    }
""",
    inputSchema={
        "type": "object",
        "properties": {
"page": {"type": "integer", "description": "The page number to retrieve."},
"page_size": {"type": "integer", "description": "The number of items per page."},
"filters": {"type": "object", "description": "Optional filters to apply to the retrieval."}
        }
    }
)

search_project_memories_tool = types.Tool(
    name="""
Search through stored project management information using semantic search (v2 API).

This tool uses the v2 search API, which supports advanced filtering capabilities.

Args:
    query: The search query string.
    filters: (Optional) A dictionary of filters to apply to the search.

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
"filters": {"type": "object", "description": "Optional filters to apply to the search."}
        },
        "required": ["query"]
    }
)

update_project_memory_tool = types.Tool(
    name="update_project_memory",
    description="""
Update an existing project memory with new content.

This tool updates a memory identified by its ID. Ideal for smaller changes
where maintaining the memory's ID and creation timestamp is important.

Guidelines for choosing update vs. delete+create:
- Use UPDATE when: making minor changes, preserving references is critical
- Consider DELETE+CREATE when: completely restructuring content
- When unsure: start with update, and if structural issues occur, fall back to delete+create

IMPORTANT NOTE: While `add_project_memory` might sometimes update existing entries 
based on internal matching logic, `update_project_memory` ensures explicit and 
intentional updates to specific entries. Use this tool when you need guaranteed
updates to an exact memory entry with full control over the process.

Args:
    memory_id: The unique identifier of the memory to update
    text: The new content for the memory

Returns:
    dict: The updated memory object with complete metadata

Example usage:
    ```
    # 1. Search for memories to update
    memories = await search_project_memories("project status")
    
    # 2. From the results, identify the ID of the memory to update
    if memories and isinstance(memories, list) and len(memories) > 0:
        memory_id = memories[0]["id"]
        original_content = memories[0].get("memory", "")
        
        # 3. Update only specific information while preserving structure
        updated_content = original_content.replace(
            "completionLevel: 0.5", 
            "completionLevel: 0.7"
        )
        
        # 4. Update the memory with explicit ID reference
        result = await update_project_memory(
            memory_id=memory_id,
            text=updated_content
        )
    ```
""",
    inputSchema={
        "type": "object",
        "properties": {
"memory_id": {"type": "string", "description": "The unique identifier of the memory to update."},
"text": {"type": "string", "description": "The new content for the memory."}
        },
        "required": ["memory_id", "text"]
    }
)

delete_project_memory_tool = types.Tool(
    name="delete_project_memory",
    description="""
    Delete a specific project memory from mem0.

    This tool removes a memory by its ID.

    Args:
        memory_id: The unique identifier of the memory to delete.

    Returns:
        str: A success message if the memory was deleted successfully, or an error message if there was an issue.
    """,
    inputSchema={
        "type": "object",
        "properties": {
            "memory_id": {"type": "string", "description": "The unique identifier of the memory to delete."}
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

# --- グローバル例外フック追加 ---
def log_unhandled_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = log_unhandled_exception
# --- ここまで ---

# --- asyncioイベントループ例外ハンドラ追加 ---
def handle_asyncio_exception(loop, context):
    logger.critical(f"Asyncio unhandled exception: {context.get('message')}", exc_info=context.get('exception'))

try:
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_asyncio_exception)
except Exception as e:
    logger.error(f"Failed to set asyncio exception handler: {e}")
# --- ここまで ---

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
    # ツール呼び出し開始ログ
    logger.info(f"★★ call_tool invoked: name={name}, args={arguments}")
    # ログを即時フラッシュ
    for h in logger.handlers:
        try:
            h.flush()
        except Exception:
            pass
    try:
        if name == "add_project_memory":
            messages = [{"role": "user", "content": arguments["text"]}]
            api_params = {
                "messages": messages,
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
            mem0_client.add(**api_params)
            return [types.TextContent(type="text", text="Successfully added project memory")]

        elif name == "get_all_project_memories":
            params = {k: v for k, v in arguments.items() if v is not None}
            # フィルタ必須項目がない場合、デフォルトで user_id を付与
            if not any(k in params for k in ["run_id", "user_id", "agent_id", "app_id"]):
                params["user_id"] = DEFAULT_USER_ID
            result = mem0_client.get_all(**params)
            return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

        elif name == "search_project_memories":
            params = {k: v for k, v in arguments.items() if v is not None}
            result = mem0_client.search(**params)
            return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

        elif name == "update_project_memory":
            params = {k: v for k, v in arguments.items() if v is not None}
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

        logger.info(f"call_tool finished: name={name}")
    except Exception as e:
        logger.exception(f"call_tool error: name={name}, args={arguments}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
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
