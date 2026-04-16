API_REQUEST_TOOL_DESCRIPTION = """
Make API requests to the Workpods backend to manage projects, tasks, milestones, and other workspace data.

## CRITICAL: All Resource Endpoints Are Workspace-Scoped

Almost every endpoint requires a `workspace_id` in the URL path. There is NO `/v1/projects` or `/v1/tasks` endpoint.

To get the user's default workspace:
```
GET /v1/workspaces/default
```
The response contains `data.id` — use that UUID as `{workspace_id}` in all subsequent calls.

## Common Mistakes (WRONG vs RIGHT)

| WRONG (404)                        | RIGHT                                                        |
|------------------------------------|--------------------------------------------------------------|
| `GET /v1/projects`                 | `GET /v1/workspaces/{workspace_id}/projects`                 |
| `POST /v1/tasks`                   | `POST /v1/workspaces/{wid}/projects/{pid}/tasks`             |
| `GET /v1/milestones`               | `GET /v1/workspaces/{wid}/projects/{pid}/milestones`         |
| `GET /v1/labels`                   | `GET /v1/workspaces/{wid}/task-labels`                       |
| `PATCH /v1/tasks/{id}`             | `PATCH /v1/workspaces/{wid}/projects/{pid}/tasks/{id}`       |

## How to Use

- **GET**: Retrieve data. Use `params` for filtering and pagination.
- **POST**: Create new records. Provide the data in `payload`.
- **PATCH**: Partially update a record. Only include changed fields in `payload`.
- **DELETE**: Remove a record. No payload needed.

## Endpoint Reference

### Workspaces
- `GET /v1/workspaces` — List user's workspaces
- `GET /v1/workspaces/default` — Get default workspace (use this first!)
- `GET /v1/workspaces/{workspace_id}` — Get workspace details
- `PATCH /v1/workspaces/{workspace_id}` — Update workspace
- `PUT /v1/workspaces/default` — Set default workspace (payload: `{"workspace_id": "..."}`)
- `POST /v1/organizations/{org_id}/workspaces` — Create workspace
- `GET /v1/workspaces/{workspace_id}/members` — List members
- `POST /v1/workspaces/{workspace_id}/members` — Invite member

### Projects (workspace-scoped)
- `GET /v1/workspaces/{wid}/projects` — List projects (params: `is_starred`, `is_archived`, `skip`, `limit`)
- `POST /v1/workspaces/{wid}/projects` — Create project
- `GET /v1/workspaces/{wid}/projects/{pid}` — Get project (includes tasks, milestones, statuses)
- `PATCH /v1/workspaces/{wid}/projects/{pid}` — Update project
- `DELETE /v1/workspaces/{wid}/projects/{pid}` — Delete project

### Tasks (project-scoped, requires workspace_id AND project_id)
- `GET /v1/workspaces/{wid}/projects/{pid}/tasks` — List tasks (params: `status_id`, `priority`, `assigned_to`, `label_id`, `search`, `skip`, `limit`)
- `POST /v1/workspaces/{wid}/projects/{pid}/tasks` — Create task
- `GET /v1/workspaces/{wid}/projects/{pid}/tasks/{tid}` — Get task
- `PATCH /v1/workspaces/{wid}/projects/{pid}/tasks/{tid}` — Update task
- `DELETE /v1/workspaces/{wid}/projects/{pid}/tasks/{tid}` — Delete task
- `PATCH /v1/workspaces/{wid}/projects/{pid}/tasks/reorder` — Reorder tasks
- `POST /v1/workspaces/{wid}/projects/{pid}/tasks/{tid}/assignees` — Add assignee (payload: `{"user_id": "..."}`)
- `DELETE /v1/workspaces/{wid}/projects/{pid}/tasks/{tid}/assignees/{user_id}` — Remove assignee
- `POST /v1/workspaces/{wid}/projects/{pid}/tasks/{tid}/labels` — Add label (payload: `{"label_id": "..."}`)
- `DELETE /v1/workspaces/{wid}/projects/{pid}/tasks/{tid}/labels/{label_id}` — Remove label
- `GET /v1/workspaces/{wid}/my-tasks` — Current user's assigned tasks

### Milestones (project-scoped)
- `GET /v1/workspaces/{wid}/projects/{pid}/milestones` — List milestones
- `POST /v1/workspaces/{wid}/projects/{pid}/milestones` — Create milestone
- `PATCH /v1/workspaces/{wid}/projects/{pid}/milestones/{mid}` — Update milestone
- `DELETE /v1/workspaces/{wid}/projects/{pid}/milestones/{mid}` — Delete milestone

### Statuses & Labels (workspace-scoped)
- `GET /v1/workspaces/{wid}/task-statuses` — List task statuses
- `GET /v1/workspaces/{wid}/project-statuses` — List project statuses
- `GET /v1/workspaces/{wid}/milestone-statuses` — List milestone statuses
- `GET /v1/workspaces/{wid}/task-labels` — List labels

### Threads (workspace-scoped)
- `GET /v1/workspaces/{wid}/threads` — List threads
- `POST /v1/workspaces/{wid}/threads` — Create thread
- `PATCH /v1/workspaces/{wid}/threads/{tid}` — Update thread

### Project Updates
- `GET /v1/workspaces/{wid}/projects/{pid}/updates` — List project updates
- `POST /v1/workspaces/{wid}/projects/{pid}/updates` — Create project update

### Files (workspace-scoped durable documents)
- `POST /v1/workspaces/{wid}/files` — Create file
- `POST /v1/workspaces/{wid}/files/directories` — Create directory
- `GET /v1/workspaces/{wid}/files/content` — Read file content
- `PATCH /v1/workspaces/{wid}/files/content` — Edit file by find/replace
- `PUT /v1/workspaces/{wid}/files/content` — Overwrite file content
- `GET /v1/workspaces/{wid}/files/info` — Get file metadata
- `GET /v1/workspaces/{wid}/files/ls` — List directory contents
- `GET /v1/workspaces/{wid}/files/search` — Search files by name
- `GET /v1/workspaces/{wid}/files/search-content` — Search files by content
- `PATCH /v1/workspaces/{wid}/files/move` — Move or rename file/directory
- `DELETE /v1/workspaces/{wid}/files` — Delete file or directory
- Prefer `home_type` and `home_id` in payloads for workspace, project, milestone, and task homes.

### Other (NOT workspace-scoped)
- `GET /v1/auth/me` — Current user profile
- `GET /v1/organizations` — List organizations
- `POST /v1/users/{user_id}/files` — Create user-home file
- `POST /v1/users/{user_id}/files/directories` — Create user-home directory
- `GET /v1/users/{user_id}/files/content` — Read user-home file content
- `GET /v1/users/{user_id}/files/ls` — List user-home directory contents
- `GET /v1/users/{user_id}/files/search` — Search user-home files
- `GET /v1/activities` — List activities
- `GET /v1/agent-instructions` — List agent instructions
- `GET /v1/skills` — List skills

## Examples

```
# Step 1: Get default workspace
api_request(method="GET", endpoint="/v1/workspaces/default")
# Response: {"status": "success", "data": {"id": "abc-123", "name": "My Workspace", ...}}

# Step 2: List projects in that workspace
api_request(method="GET", endpoint="/v1/workspaces/abc-123/projects")

# Step 3: Create a task in a project
api_request(method="POST", endpoint="/v1/workspaces/abc-123/projects/proj-456/tasks", payload={"title": "Design mockup", "priority": "high"})

# Step 4: Update task status
api_request(method="PATCH", endpoint="/v1/workspaces/abc-123/projects/proj-456/tasks/task-789", payload={"status_id": "status-uuid-here"})

# Get current user's tasks across all projects
api_request(method="GET", endpoint="/v1/workspaces/abc-123/my-tasks")

# Filter tasks by priority
api_request(method="GET", endpoint="/v1/workspaces/abc-123/projects/proj-456/tasks", params={"priority": "high"})

# Create a durable workspace file
api_request(method="POST", endpoint="/v1/workspaces/abc-123/files", payload={"path":"/plans/resource-plan.md","content":"# Resource Plan","home_type":"workspace","home_id":"abc-123"})

# Overwrite a project-scoped durable file
api_request(method="PUT", endpoint="/v1/workspaces/abc-123/files/content", payload={"path":"/briefs/project-brief.md","content":"# Updated Brief","home_type":"project","home_id":"proj-456"})
```

## Display Name (`display_name`)

The `display_name` appears in the user's chat as a status label. Write it in plain,
action-oriented language that tells the user what you're doing — not how.

Rules:
- Never use endpoints, IDs, HTTP methods, or technical terms
- Use present participle form ("Fetching...", "Updating...", "Creating...")
- Be specific to the business action
- Keep it under 6 words

Examples:
  GOOD: "Fetching your projects", "Updating task status", "Creating a new milestone",
        "Looking up team members", "Saving your changes"
  BAD:  "Making API request", "GET /v1/workspaces/abc/tasks", "PATCH task",
        "Querying database", "POST request"

## Important
- Always resolve workspace_id first via `GET /v1/workspaces/default` before making resource calls.
- Use PATCH over PUT when only updating specific fields.
- `status_id` fields expect a UUID — fetch valid statuses from the relevant status endpoint first.
- `priority` is a string: "urgent", "high", "medium", "low", or "none".
- Task assignees and labels are managed via sub-resource endpoints, not in the task payload.
- Confirm destructive operations (DELETE) with the user before executing."""
