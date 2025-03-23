from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
import uvicorn
from mem0 import MemoryClient
from dotenv import load_dotenv
import json
from typing import List, Dict, Union

load_dotenv()

# Initialize FastMCP server for mem0 tools
mcp = FastMCP("mem0-mcp")

# Initialize mem0 client and set default user
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

@mcp.tool(
    description="""Add or update structured project information in mem0 using v2 API.

    This tool adds project information to mem0, utilizing the v2 API for enhanced features and performance.
    If the information already exists (based on internal mem0 logic), it may be automatically updated.

    For explicit updates, use the `update_project_memory` tool (to be implemented).

    This tool is designed to store the following types of project information:
    - Project Status
    - Task Management
    - Decision Records
    - Resource Allocation
    - Risk Assessment
    - Technical Artifacts

    Information should be formatted according to the templates defined in Memory Structure and Templates, using structured data formats (JavaScript objects, JSON, YAML), and include project name and timestamp as metadata.

    Relationships between items should be described using keys such as 'relatedTo', 'enables', 'blockedBy', etc., in string format.

    Args:
        text: The project information to add or update. It should be formatted according to the templates defined in Memory Structure and Templates, using structured data formats (JavaScript objects, JSON, YAML).

    Returns:
        str: A success message if the project information was added or updated successfully, or an error message if there was an issue.
    """
)
async def add_project_memory(text: str) -> str:
    """Add new project management information to mem0.

    This tool is designed to store structured project information including:
    - Project Status
    - Task Management
    - Decision Records
    - Resource Allocation
    - Risk Assessment
    - Technical Artifacts

    Information should be formatted according to the templates defined in Memory Structure and Templates, using structured data formats (JavaScript objects, JSON, YAML), and include project name and timestamp as metadata.

    Relationships between items should be described using keys such as 'relatedTo', 'enables', 'blockedBy', etc., in string format.

    Args:
        text: The project information to add to mem0. It should be formatted according to the templates defined in Memory Structure and Templates, using structured data formats (JavaScript objects, JSON, YAML), and include project name and timestamp as metadata. Metadata should be added at the top level of the object using the `project` key and `timestamp` key.

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
    """
    try:
        messages = [{"role": "user", "content": text}]
        mem0_client.add(messages, user_id=DEFAULT_USER_ID, output_format="v1.1", version="v2")
        return f"Successfully added project information: {text}"
    except Exception as e:
        return f"Error adding project information: {str(e)}"

@mcp.tool(
    description="""Retrieve all stored project management information for the default user (v2 API).

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
    """
)
async def get_all_project_memories(page: int = 1, page_size: int = 50, filters: dict = None) -> Union[List[Dict], Dict]:
    try:
        # Fetch memory data from mem0 client
        response = mem0_client.get_all(
            user_id=DEFAULT_USER_ID, 
            page=page, 
            page_size=page_size, 
            version="v2", 
            filters=filters
        )
        
        # API からのレスポンスをそのまま返す
        return response
    except Exception as e:
        print(f"Error in get_all_project_memories: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {getattr(e, '__dict__', {})}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        return {"error": f"Error retrieving project information: {str(e)}"}

@mcp.tool(
    description="""Search through stored project management information using semantic search (v2 API).

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
    """
)
async def search_project_memories(query: str, filters: dict = None) -> List[Dict]:
    try:
        memories = mem0_client.search(query, user_id=DEFAULT_USER_ID, version="v2", filters=filters)
        
        # API からのレスポンスをそのまま返す
        return memories
    except Exception as e:
        print(f"Error in search_project_memories: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {getattr(e, '__dict__', {})}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        return {"error": f"Error searching project information: {str(e)}"}

@mcp.tool(
    description="""Delete a specific project memory from mem0.

    This tool removes a memory by its ID.

    Args:
        memory_id: The unique identifier of the memory to delete.

    Returns:
        str: A success message if the memory was deleted successfully, or an error message if there was an issue.
    """
)
async def delete_project_memory(memory_id: str) -> str:
    """Delete a specific project memory from mem0.
    
    This tool removes the specified memory from the mem0 database.
    
    Args:
        memory_id: The unique identifier of the memory to delete.
        
    Returns:
        str: A success message if the memory was deleted successfully, or an error message if there was an issue.
    """
    try:
        mem0_client.delete(memory_id=memory_id)
        return f"Successfully deleted project memory with ID: {memory_id}"
    except Exception as e:
        print(f"Error in delete_project_memory: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {getattr(e, '__dict__', {})}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        return f"Error deleting project memory: {str(e)}"
    
@mcp.tool(
    description="""Extract memory IDs from the results of get_all_project_memories or search_project_memories.

    This utility tool helps extract memory IDs that can be used with delete operations.

    Args:
        memories: A list of memory objects or paginated response from memory retrieval operations.

    Returns:
        list: A list of memory IDs that can be used with delete_project_memory.
    """
)
async def extract_memory_ids(memories: Union[List[Dict], Dict]) -> List[str]:
    """Extract memory IDs from memory retrieval results.
    
    This tool simplifies the extraction of memory IDs from complex API responses.
    
    Args:
        memories: Response from get_all_project_memories or search_project_memories
        
    Returns:
        list: List of memory IDs
    """
    try:
        # ページネーション結果の場合
        if isinstance(memories, dict) and "results" in memories:
            memory_list = memories["results"]
        # 直接リストが返された場合
        elif isinstance(memories, list):
            memory_list = memories
        # エラーレスポンスなど、想定外の形式の場合
        else:
            return {"error": "Unexpected format in memories parameter"}
        
        # 各メモリからIDを抽出
        memory_ids = []
        for memory in memory_list:
            if isinstance(memory, dict) and "id" in memory:
                memory_ids.append(memory["id"])
        
        return memory_ids
    except Exception as e:
        return {"error": f"Failed to extract memory IDs: {str(e)}"}

# Delete multi posts at once, not tested yet.
@mcp.tool(
    description="""Delete multiple project memories based on specified filters.

    This tool uses the delete_all method to remove multiple memories based on filter criteria.
    IMPORTANT: Use this tool with caution as it will delete ALL memories that match the specified filters.
    If no filters are specified, it could potentially delete ALL memories.

    Args:
        user_id (str, optional): Filter memories by user ID.
        agent_id (str, optional): Filter memories by agent ID.
        app_id (str, optional): Filter memories by app ID.
        run_id (str, optional): Filter memories by run ID.
        metadata (dict, optional): Filter memories by metadata.
        org_id (str, optional): Filter memories by organization ID.
        project_id (str, optional): Filter memories by project ID.

    Returns:
        str: A success message if the memories were deleted successfully, or an error message if there was an issue.
    """
)
async def delete_all_project_memories(
    user_id: str = None,
    agent_id: str = None,
    app_id: str = None,
    run_id: str = None,
    metadata: dict = None,
    org_id: str = None,
    project_id: str = None
) -> str:
    """Delete multiple project memories based on specified filters.
    
    This tool removes multiple memories from the mem0 database based on provided filters.
    If no filters are specified, it could potentially delete ALL memories, so use with caution.
    
    Args:
        user_id (str, optional): Filter memories by user ID.
        agent_id (str, optional): Filter memories by agent ID.
        app_id (str, optional): Filter memories by app ID.
        run_id (str, optional): Filter memories by run ID.
        metadata (dict, optional): Filter memories by metadata.
        org_id (str, optional): Filter memories by organization ID.
        project_id (str, optional): Filter memories by project ID.
        
    Returns:
        str: A success message if the memories were deleted successfully, or an error message if there was an issue.
    """
    try:
        # フィルタパラメータの辞書を構築（Noneでないパラメータのみ）
        filter_params = {}
        if user_id is not None:
            filter_params['user_id'] = user_id
        if agent_id is not None:
            filter_params['agent_id'] = agent_id
        if app_id is not None:
            filter_params['app_id'] = app_id
        if run_id is not None:
            filter_params['run_id'] = run_id
        if metadata is not None:
            filter_params['metadata'] = metadata
        if org_id is not None:
            filter_params['org_id'] = org_id
        if project_id is not None:
            filter_params['project_id'] = project_id
            
        # フィルタ条件の説明を生成（ログとレスポンス用）
        filter_description = ", ".join([f"{k}={v}" for k, v in filter_params.items()]) if filter_params else "no filters (ALL memories)"
        
        # APIクライアントを使用して削除を実行
        mem0_client.delete_all(**filter_params)
        
        return f"Successfully deleted project memories with filters: {filter_description}"
    except Exception as e:
        print(f"Error in delete_all_project_memories: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {getattr(e, '__dict__', {})}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        return f"Error deleting project memories: {str(e)}"

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can server the provied mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


if __name__ == "__main__":
    mcp_server = mcp._mcp_server

    import argparse

    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    args = parser.parse_args()

    # Bind SSE request handling to MCP server
    starlette_app = create_starlette_app(mcp_server, debug=True)

    uvicorn.run(starlette_app, host=args.host, port=args.port)
