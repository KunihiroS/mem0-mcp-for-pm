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

# Metadata Extraction (when available)
- Temporal Context: Extract timestamps, durations, deadlines, and sequence information.
- Project Context: Identify project names, phases, domains, and scope indicators.
- Relationship Mapping: Determine relationships between extracted elements (dependencies, etc.).

# Interpretation Guidelines
- For structured input (JavaScript/JSON objects): Preserve the structural hierarchy while enriching with contextual metadata.
- For code-structured representations: Analyze both the structural patterns and the semantic content.
- For mixed-format input: Prioritize semantic content while acknowledging structural hints.

# Output Structure Formation
- Maintain consistent categorization across multiple records.
- Preserve original identifiers and reference keys for continuity.
- Generate contextually appropriate metadata when implicit in the source.
- Structure output to facilitate future retrieval, updating, and relationship mapping.
"""
mem0_client.update_project(custom_instructions=CUSTOM_INSTRUCTIONS)

@mcp.tool(
    description="""Add new project management information to mem0. This tool stores project status, task management, 
    decision records, and other project-related information for future reference. When adding information, include:
    - Project Status: Progress state, completion levels, and overall status
    - Task Management: Tasks with priorities, dependencies, and statuses
    - Decision Records: Decisions with rationale and implications
    - Resource Allocation: Team, infrastructure, and budget information
    - Risk Assessment: Potential risks and mitigation strategies
    - Technical Artifacts: System architecture, technologies, and standards
    Information is typically structured as JavaScript objects with appropriate metadata (project, timestamp),
    and will be indexed for semantic search and retrieval using natural language queries."""
)
async def add_project_memory(text: str) -> str:
    """Add new project management information to mem0.
    
    This tool is designed to store structured project information including:
    - Project status updates
    - Task management details
    - Decision records with rationale
    - Resource allocation information
    - Risk assessments
    - Technical specifications
    
    Information should be formatted as JavaScript objects with appropriate
    metadata comments for project identification and timestamps.

    Args:
        text: The project management information to store, formatted as JavaScript objects
    """
    try:
        messages = [{"role": "user", "content": text}]
        mem0_client.add(messages, user_id=DEFAULT_USER_ID, output_format="v1.1")
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
