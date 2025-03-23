# mem0 MCP Server for project management

mem0 MCP Server is a bridge between MCP Host applications and the mem0 cloud service, providing memory capabilities for MCP Host AI.

This is forked in order to change the scope from coding to project management.
The forked deals more higher level context related with project management topics.

Additionally, this forked experimentally integrate cording format into high level context like human protocol.

## Features

- Forked in order to change the usage from original coding scope to project management scope.
- Project memory storage and retrieval
- Semantic search for finding relevant project information
- Structured project management data handling

## Installation and usage

### Pre-condition and requirement

- Python 12.0 or newer,
- mcp-proxy (in case Cline or Roo code)


### Details

1. Clone the repository and move into.

2. Set up virtual environment using `uv`.

```bash
uv venv --python 3.12
```
3. Activate virtual environment using `uv`.

```bash
source .venv/bin/activate
```

4. Install the dependencies using `uv`.

```bash
# Install in editable mode from pyproject.toml
uv pip install -e .
```

5. Create .gitignore in repo root.

```bash
touch .gitignore
```

6. Update .gitignore

```sample
# Python
__pycache__/
*.py[cod]
*.egg-info/

# Environment variables
.env

# Egg info
mem0_mcp.egg-info/
```

7. Create .env in repo root.

```bash
touch .env
```

8. Update .env

```
MEM0_API_KEY={your API Key}
```

9. Clone and install the following OSS.

https://github.com/sparfenyuk/mcp-proxy

10. Add MCP Server settings.

- Cline

```cline_mcp_settings.json
"mem0": {
      "command": "PATH_TO/mcp-proxy", # ex: /home/{user}/.local/bin/mcp-proxy
      "args": [
        "http://127.0.0.1:6789/sse" # configure port as you need
      ]
    }
```

11. Launch MCP Server (activated virtual env required)

```bash
python main.py --host 127.0.0.1 --port 6789
```

12. Check the functionality by MCP Host (like Cline)

```
Hey, can you get all memories on mem0?
```

## Operation

- Ensure run MCP Server fast.
- There are several ways automatic run server, like adding script .bashrc
- Set up automatic as your environment is easier usage.

## Available Tools

- add_project_memory: Add new project management information
- get_all_project_memories: Retrieve all stored project information
- search_project_memories: Search for specific project information

## Technical details

The uniqueness of this forked is the structured format between MCP Host and mem0 is expected in coding format like Javascript object.
Make sure you set the custom instruction to be able to handle better.

## Custom instruction

In order to make mem0 working as fitting to project management purpose, this forked has the following instruction for AI.

### For mem0

- Check the source code.

### For MCP Host

- The following is just sample, find the best by yourself !!

---

# mem0 Guide for Effective Project Memory (Revised)

**You can manage your memory by using the mem0 MCP Server**

---

## Important

The mem0 server extracts the following information from your input. To ensure effective extraction, use structured data formats (e.g., JavaScript objects, JSON, or YAML).

- **Project Status**: Current progress, completion levels, and overall status.
- **Task Management**: Tasks with priorities, dependencies, statuses, and deadlines.
- **Decision Records**: Decisions, their rationale, implications, and constraints.
- **Resource Allocation**: Resource usage, assignments, and availability.
- **Risk Assessment**: Potential risks, impact ratings, and mitigation strategies.
- **Technical Artifacts**: Technical specifications, dependencies, and implementation notes.

---

## Memory Structure and Templates

Use the following templates to structure memory entries. Each template has a clear purpose, with mandatory and optional fields defined for flexibility.

### 1. Project Status

**Purpose**: Track overall project progress and current focus.  
**Mandatory Fields**: `name`, `purpose`  
**Optional Fields**: `version`, `phase`, `completionLevel`, `milestones`, `currentFocus`

```javascript
// [PROJECT: project-name] [TIMESTAMP: yyyy-MM-ddTHH:mm:ss+09:00]
const projectStatus = {
  overview: {
    name: "Project Name",  // Mandatory
    purpose: "Brief description",  // Mandatory
    version: "1.2.0",  // Optional
    phase: "development"  // Optional
  },
  progress: {
    completionLevel: 0.65,  // Optional
    milestones: [  // Optional
      { name: "Planning", status: "completed", date: "2025-02-15" },
      { name: "Development", status: "in-progress", progress: 0.70 }
    ]
  },
  currentFocus: [  // Optional
    "Feature implementation for module X",
    "Performance optimization of component Y"
  ]
};
```

**Python Example**:
```python
# [PROJECT: project-name] [TIMESTAMP: yyyy-MM-ddTHH:mm:ss+09:00]
project_status = {
  "overview": {
    "name": "Project Name",  # Mandatory
    "purpose": "Brief description",  # Mandatory
    "version": "1.2.0",  # Optional
    "phase": "development"  # Optional
  }
}
```

---

### 2. Task Management

**Purpose**: Manage task priorities, statuses, and dependencies.  
**Mandatory Fields**: `description`, `status`  
**Optional Fields**: `deadline`, `assignee`, `dependencies`

```javascript
// [PROJECT: project-name] [TIMESTAMP: yyyy-MM-ddTHH:mm:ss+09:00]
const taskManagement = {
  highPriority: [
    {
      description: "Implement feature X",  // Mandatory
      status: "in-progress",  // Mandatory
      deadline: "2025-03-15",  // Optional
      assignee: "Team A",  // Optional
      dependencies: "Component Y ready"  // Optional, use string
    }
  ],
  mediumPriority: [],
  completedTasks: [
    {
      description: "Setup development environment",  // Mandatory
      status: "completed"  // Mandatory
    }
  ]
};
```

---

## Memory Update Guidelines

Follow these guidelines when updating memory.

### Metadata Enrichment

**Instruction**: Always include project name and timestamp. Add additional context (e.g., phase, sprint) as needed.  
**Example**:
```javascript
// [PROJECT: inventory-system] [TIMESTAMP: 2025-03-10T14:30:00+09:00] [PHASE: Development] [SPRINT: 3]
```

---

### Relationship Mapping

**Instruction**: Explicitly state relationships between items using strings. mem0 extracts relationship information as searchable keywords. For example, searching for 'relatedTo User Authentication' will return items that have 'User Authentication' in their `relatedTo` field.  
**Example**:
```javascript
const featureImplementation = {
  name: "Shopping Cart API",
  relatedTo: "User Authentication, Product Catalog",
  enables: "Checkout Process, Order Management",
  blockedBy: "Payment Gateway Integration"
};
```

---

### Temporal Context

**Instruction**: Use ISO 8601 format for dates and explicitly state related events.  
**Example**:
```javascript
const milestone = {
  name: "Beta Release",
  plannedDate: "2025-04-15T00:00:00+09:00",
  expectedDuration: "2 weeks",
  prerequisites: "Feature X, Feature Y",
  subsequentEvents: "User Testing, Feedback Collection"
};
```

---

### Structure for Searchability

**Instruction**: Use consistent terminology, include keywords in property names, and use descriptive variable names.  
**Example**:
```javascript
const taskManagement = {
  highPriorityTasks: [
    { description: "Implement login feature", status: "in-progress" }
  ]
};
```

---

## Enhanced Memory Access Methods

Use `search_project_memories` with queries like the following examples.

**Query Examples**:
```javascript
search_project_memories("projectStatus [PROJECT: current-project]");  // Search project status
search_project_memories("taskManagement highPriority");  // Search high-priority tasks
search_project_memories("decisionRecord database");  // Search database decisions
search_project_memories("riskAssessment high");  // Search high risks
search_project_memories("milestone Beta Release");  // Search for a specific milestone
```

**Query Creation Instructions**:
- Use category names (e.g., `projectStatus`) to narrow the search.
- Include specific keywords or phrases.
- Use project identifiers and timestamps for context.

---

## Basic Principles

### Thorough Project Identification

**Instruction**: Include a project identifier in every memory entry.  
**Example**:
```javascript
// [PROJECT: inventory-system]
```

### Integrated Chronological Management

**Instruction**: Attach an accurate timestamp to every entry.  
**Example**:
```javascript
// [TIMESTAMP: 2025-03-09T00:46:36+09:00]
```

### User-Driven Memory Operations

**Instruction**: Interpret natural language and follow user instructions.  
**Examples**:
- "Update memory" → Use `add_project_memory` to update.
- "Record progress" → Save current progress.
- "Tell me the project status" → Summarize project status.

---

## Writing Memories

Use `add_project_memory` to add information. Other tools (e.g., `search_project_memories`, `get_all_project_memories`) can be used as needed.

**JavaScript Example**:
```javascript
add_project_memory("// [PROJECT: current-project] [TIMESTAMP: 2025-03-09T00:46:36+09:00]\nconst projectStatus = {\n  overview: { name: 'Project Name', purpose: 'Brief description' }\n};");
```

**Python Example**:
```python
add_project_memory("# [PROJECT: current-project] [TIMESTAMP: 2025-03-09T00:46:36+09:00]\nproject_status = {'overview': {'name': 'Project Name', 'purpose': 'Brief description'}}")
```

**Additional Tool Examples**:
```javascript
get_all_project_memories();  // Retrieve all extracted project information
search_project_memories("decisionRecord");  // Find all decision records
```

---

## Important Notes

- **Metadata**: Always include project name (e.g., `[PROJECT: project-name]`) and timestamp (e.g., `[TIMESTAMP: yyyy-MM-ddTHH:mm:ss+09:00]`).
- **Data Format**: Use structured formats (e.g., JavaScript objects, JSON, YAML).
- **`get_all_project_memories` Output**: Returns extracted information (e.g., project name, task descriptions, statuses), not raw input.
