# mem0 MCP Server for Project Management

**Version: 0.3.1**

mem0 MCP Server bridges MCP Host applications and the mem0 cloud service, enabling structured project memory management and semantic search for project-related information.

---

## Release Notes

### v0.3.1
- Fix: "add project memory" tool to works properly by adjusting message format to mem0 API.

### v0.3.0

- Fix: as mem0 cloud service has changed the way of handling data, the way of handling data has been changed.
- Change from JavaScript object-based templates to TOML-based templates and guide, which is more efficient for data extraction by mem0 cloud service.
- Added logging functionality (check MCP Host Configuration section for details).

### v0.2.0

- Switched from SSE-based to stdio-based invocation for better compatibility with MCP Hosts
- Added support for pipx-based installation and execution
- Simplified deployment via `pyproject.toml` script entrypoint

---

## Features

- Project memory storage and retrieval
- Semantic search for project information
- Structured project management data handling
- Fully tested stdio-based MCP Server tools
- Flexible logging: stderr by default, file output via `--logfile`
- Smart CLI invocation via pipx-compatible interface

---

## MCP Host Configuration

When running this MCP Server, you **must explicitly specify the log output mode and (if enabled) the absolute log file path via command-line arguments**.

- `--log=off` : Disable all logging (no logs are written)
- `--log=on --logfile=/absolute/path/to/logfile.log` : Enable logging and write logs to the specified absolute file path
- Both arguments are **required** when logging is enabled. The server will exit with an error if either is missing, the path is not absolute, or if invalid values are given.

### Example: Logging Disabled
```json
"mem0": {
  "command": "pipx",
  "args": ["run", "mem0-mcp-for-pm", "--log=off"],
  "env": {
    "MEM0_API_KEY": "{apikey}"
  }
}
```

### Example: Logging Enabled (absolute log file path required)
```json
"mem0": {
  "command": "pipx",
  "args": ["run", "mem0-mcp-for-pm", "--log=on", "--logfile=/workspace/logs/mem0-mcp-server.log"],
  "env": {
    "MEM0_API_KEY": "{apikey}"
  }
}
```

> **Note:**
> - When logging is enabled, logs are written **only** to the specified absolute file path. Relative paths or omission of `--logfile` will cause an error.
> - When logging is disabled, no logs are output.
> - If the required arguments are missing or invalid, the server will not start and will print an error message.
> - The log file must be accessible and writable by the MCP Server process.

---

## Tools

- `add_project_memory`
- `get_all_project_memories`
- `search_project_memories`
- `update_project_memory`
- `delete_project_memory`
- `delete_all_project_memories`

All tools are available via stdio-based MCP protocol.

---

## Logging

- Default: stderr
- Optional: `--logfile /path/to/logfile.log`

---

## License

See LICENSE file.

## Technical details

The uniqueness of this forked is the structured format between MCP Host and mem0 is expected in coding format like TOML.
Make sure you set the custom instruction to be able to handle better.

## Custom instruction

In order to make mem0 working as fitting to project management purpose, this forked has the following instruction for AI.

### For mem0

- Check the source code.

### For MCP Host

To register project information in mem0, always use the TOML format for all entries.  
Follow these guidelines to ensure optimal AI extraction, searchability, and project management usability:

#### 1. Use TOML as the Base Format

- All project memory entries must be provided as TOML-formatted strings.
- Always include at least the following top-level fields:
  - `category` (e.g., "Task Management", "Project Status", etc.)
  - `project` (project name)
  - `timestamp` (ISO 8601 format, e.g., "2025-04-29T16:00:00+09:00")

#### 2. Recommended Templates

Below are TOML templates for common project management use cases.  
Adapt these as needed, but keep the structure and metadata consistent for better search and extraction.

**Project Status Example**
```toml
category = "Project Status"
project = "project-name"
timestamp = "2025-04-29T16:00:00+09:00"
name = "Project Name"
purpose = "Project Purpose"
version = "1.2.0"
phase = "development"
completionLevel = 0.65
milestones = ["Planning", "Development"]
currentFocus = ["Implementing Feature X", "Optimizing Component Y"]

[metadata]
type = "status"
priority = "high"
tags = ["backend", "release"]
```

**Task Management Example**
```toml
category = "Task Management"
project = "project-name"
timestamp = "2025-04-29T16:00:00+09:00"

[[tasks]]
description = "Implement Feature X"
status = "in-progress"
deadline = "2025-05-15"
assignee = "Team A"
dependencies = ["Component Y"]

[metadata]
type = "task"
priority = "high"
tags = ["frontend", "authentication"]
```

#### 3. Context Management with run_id

- Use the `run_id` parameter to logically group related entries.
- Recommended format:  
  `project:project-name:category:subcategory`
- Example:
  ```
  run_id = "project:member-system:feature:authentication"
  ```

#### 4. Metadata Usage

- Always add a `[metadata]` TOML table to enhance search and filtering.
- Example:
  ```toml
  [metadata]
  type = "task"
  priority = "high"
  tags = ["frontend"]
  ```

#### 5. Information Lifecycle

- Use `immutable = true` to prevent updates.
- Use `expiration_date = "YYYY-MM-DD"` to set expiry.

#### 6. Best Practices

- Be consistent with field names and structure.
- Always include `project` and `timestamp`.
- Use clear, descriptive tags and metadata.
- Leverage TOML comments for human/AI hints if needed.

---

By following these TOML-based guidelines, you will maximize the effectiveness of mem0’s project memory extraction and management.  
For more advanced use cases, refer to the source code and server-side custom instructions.

- The following is just sample, find the best by yourself !!
---

# mem0 Guide for Effective Project Memory (Enhanced)

This guide outlines strategies and templates for effectively managing project information using mem0. The aim is to improve searchability and reusability of project data through structured templates and metadata management.

## Information Structure and Templates

mem0 can effectively manage the following types of information. Using structured templates improves searchability and reusability. Note that the templates provided are examples and should be adapted to fit specific project needs.

### 1. Project Status Management

**Template**:
```toml
category = "Project Status"
project = "project-name"
timestamp = "2025-04-29T16:00:00+09:00"
name = "Project Name"
purpose = "Project Purpose"
version = "1.2.0"
phase = "development"
completionLevel = 0.65
milestones = ["Planning Phase", "Development Phase"]
currentFocus = ["Implementing Feature X", "Optimizing Component Y"]
risks = ["Concerns about API stability", "Resource shortage"]
```

### 2. Task Management

**Template**:
```toml
category = "Task Management"
project = "project-name"
timestamp = "2025-04-29T16:00:00+09:00"

[[tasks]]
description = "Implement Feature X"
status = "in-progress"
deadline = "2025-03-15"
assignee = "Team A"
dependencies = ["Component Y"]

[[tasks]]
description = "Setup Development Environment"
status = "completed"
```

### 3. Meeting Summary

**Template**:
```toml
category = "Meeting Summary"
project = "project-name"
timestamp = "2025-04-29T16:00:00+09:00"
title = "Weekly Progress Meeting"
date = "2025-03-23"
attendees = ["Sato", "Suzuki", "Tanaka"]
topics = ["Progress Report", "Risk Management", "Next Week's Plan"]
decisions = ["Approve additional resource allocation", "Delay release date by one week"]
[[actionItems]]
description = "Procedure for adding resources"
assignee = "Sato"
dueDate = "2025-03-25"
[[actionItems]]
description = "Revise test plan"
assignee = "Suzuki"
dueDate = "2025-03-24"
```

## Effective Information Management Techniques

### 1. Context Management (run_id)

Using mem0's `run_id` parameter, you can logically group related information. This helps maintain specific conversation flows or project contexts.

**Recommended Format**:
```
project:project-name:category:subcategory
```

**Usage Example**:
```toml
run_id = "project:member-system:feature:authentication"
```

### 2. Effective Use of Metadata

Using metadata can enhance the searchability of information. We recommend using the following schema:
```toml
[metadata]
type = "meeting|task|decision|status|risk"
priority = "high|medium|low"
tags = ["frontend", "backend", "design"]
status = "pending|in-progress|completed"
```

### 3. Information Lifecycle Management

Using the `immutable` and `expiration_date` parameters, you can manage the lifecycle of information.

**Usage Example**:
```toml
immutable = true
expiration_date = "2025-06-30"
```

## Practical Usage Patterns

### 1. Sprint Management Example
```toml
category = "Project Status"
project = "member-system"
timestamp = "2025-05-01T10:00:00+09:00"
sprint = "Sprint-2025-05"
duration = "2 weeks"
goals = ["Implement authentication feature", "Improve UI"]
[[tasks]]
description = "Implement login screen"
assignee = "Tanaka"
estimate = "3 days"
[[tasks]]
description = "API integration"
assignee = "Sato"
estimate = "2 days"
[metadata]
type = "status"
tags = ["sprint-planning"]
```

```toml
category = "Project Status"
project = "member-system"
timestamp = "2025-05-08T15:00:00+09:00"
sprint = "Sprint-2025-05"
completionLevel = 0.4
[[status]]
task = "Implement login screen"
progress = 0.7
status = "in-progress"
[[status]]
task = "API integration"
progress = 0.2
status = "in-progress"
blockers = ["Change in API response specification"]
[metadata]
type = "status"
tags = ["sprint-progress"]
```

### 2. Risk Management Example
```toml
category = "Risk Management"
project = "member-system"
timestamp = "2025-05-03T11:00:00+09:00"
[[risks]]
description = "Concerns about external API stability"
impact = "High"
probability = "Medium"
mitigation = "Implement fallback mechanism"
owner = "Development Lead"
status = "open"
[metadata]
type = "risk"
priority = "high"
```

```toml
category = "Risk Management"
project = "member-system"
timestamp = "2025-05-10T16:30:00+09:00"
[[risks]]
description = "Concerns about external API stability"
status = "Resolved"
resolution = "Fallback mechanism implementation completed"
[metadata]
type = "risk"
priority = "medium"
```

## Important Points

- **Standard Metadata**: Always include the project name and timestamp.
- **Data Format**: Use TOML for all entries, and include a `[metadata]` table.
- **Context Management**: Use `run_id` hierarchically to maintain information relevance.
- **Search Efficiency**: Consistent metadata and structure improve search efficiency.

## 4. Implementation Strategy

To implement the above improvements, we recommend the following steps:

1. **Enhance the `add_project_memory` Method**:
   - Update documentation strings: Improve usage examples and parameter descriptions.
   - Error handling: Provide more detailed error information.
   - Response format: Explicitly state the parameters used.

2. **Update Custom Instructions**:
   - Enrich template examples.
   - Clarify recommended usage of `run_id` (introduce hierarchical structure).
   - Standardize metadata schema.
   - Provide practical usage examples.

These improvements will enhance the usability and efficiency of information management while maintaining compatibility with existing APIs.

## 5. Summary

The proposed improvements provide value in the following ways while maintaining compatibility with existing mem0 MCP server functions: