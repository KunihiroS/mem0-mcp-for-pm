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
    description="""Retrieve all stored project management information for the default user. Call this tool when you need 
    comprehensive context of previously stored project data. This is useful when:
    - You need to review the overall project status
    - You want to check all tasks and their current statuses
    - You need to review previous decisions and their rationale
    - You want to ensure no relevant project information is missed
    Returns a comprehensive list of:
    - Project status information
    - Task management details
    - Decision records
    - Resource allocation data
    - Risk assessments
    - Technical specifications
    Results are returned in JSON format with metadata."""
)
async def get_all_project_memories() -> str:
    """Get all project management information for the default user.

    Returns a JSON formatted list of all stored project data, including:
    - Project status information
    - Task management details
    - Decision records
    - Resource allocation data
    - Risk assessments
    - Technical specifications
    Each entry includes metadata about when it was created and its content type.
    """
    try:
        memories = mem0_client.get_all(user_id=DEFAULT_USER_ID, page=1, page_size=50)
        flattened_memories = [memory["memory"] for memory in memories["results"]]
        return json.dumps(flattened_memories, indent=2)
    except Exception as e:
        return f"Error retrieving project information: {str(e)}"

@mcp.tool(
    description="""Search through stored project management information using semantic search. This tool should be called 
    for user queries to find relevant project data. It helps find:
    - Project status information
    - Task management details
    - Decision records and their rationale
    - Resource allocation data
    - Risk assessments and mitigation strategies
    - Technical specifications and architecture details
    The search uses natural language understanding to find relevant matches, so you can
    describe what you're looking for in plain English. Always search the project memory before 
    providing answers to ensure you leverage existing knowledge."""
)
async def search_project_memories(query: str) -> str:
    """Search project management information using semantic search.

    The search is powered by natural language understanding, allowing you to find:
    - Project status updates
    - Task management information
    - Decision records
    - Resource allocation details
    - Risk assessments
    - Technical documentation
    Results are ranked by relevance to your query.

    Args:
        query: Search query string describing what you're looking for. Can be natural language
              or specific technical terms.
    """
    try:
        memories = mem0_client.search(query, user_id=DEFAULT_USER_ID, output_format="v1.1")
        flattened_memories = [memory["memory"] for memory in memories["results"]]
        return json.dumps(flattened_memories, indent=2)
    except Exception as e:
        return f"Error searching project information: {str(e)}"

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
