# ADA Project Agent Harness

## Core Principle

**Agent = Model + Harness**

The model contains the intelligence. The harness makes that intelligence useful. Everything in this system that is not the LLM itself — the prompts, tools, skills, orchestration logic, middleware, file systems, and sub-agent spawning — is the **harness**. The model reasons and generates text; the harness gives it state, execution, feedback loops, and enforceable constraints.

---

## High-Level Overview

**User** → **Harness (Model + Skills + Tools + Sub Agents)** → **User**

1. The **User** sends a request via chat.
2. The **Harness** wraps the request with context (middleware), routes it to the **Model**, and orchestrates the Model's interaction with **Skills**, **Tools**, and **Sub Agents**.
3. The **Harness** delivers the final response (text, documents, diagrams) back to the **User**.

---

## Harness Components

### 1. System Prompt — `src/prompt/prompt.py`

The system prompt is the harness's primary mechanism for injecting priors and constraints into the model's behavior. It defines how the model should reason, what rules to follow, and what workflows to execute.

**Intent Classification** — The prompt instructs the model to classify every incoming request:

- **Category A (Direct Response)** — Greetings, small talk, general questions. The model responds directly with no tool use.
- **Category B-Lite (Quick Tool Use)** — Simple lookups requiring 1–2 tool calls.
- **Category C (Structured Execution)** — Complex, multi-step work that enters the Cognitive Loop.

**Cognitive Loop (Category C)** — A prompt-engineered ReAct loop that structures the model's reasoning for complex tasks:

1. **THINK** — Understand the task (max 40 words).
2. **PLAN** — Create a todo list of steps.
3. **ACT** — Execute the current in-progress task via tool calls.
4. **REFLECT** — Assess findings and determine next steps. Loop back to THINK if tasks remain.

This is the harness guiding the model through a structured feedback loop rather than letting it free-associate through a complex problem.

**Document Generation Workflow** — A harness-defined 7-step orchestration process for document creation:

- Step 0: Classify scope of the document request.
- Step 1: Delegate to the Planner sub-agent.
- Step 2: Launch parallel Researcher sub-agents to fill knowledge gaps.
- Step 3: Merge all research into a single reference.
- Step 4: Present the plan to the user for approval.
- Step 5: Launch parallel Writer sub-agents for each section.
- Step 6: Generate diagrams via script execution.
- Step 7: Merge all sections into the final document.

**Core Rules** — Enforceable constraints injected via the prompt:

- No preamble, no fabrication.
- Read before write, mirror user language.
- Mark data gaps honestly.

---

### 2. Middleware Layer — Harness Hooks for Context Engineering

Middleware runs deterministically before the model sees any request. This is classic harness-level logic — the model doesn't choose what context it receives; the harness assembles it.

- **Dynamic Model Selector** — Routes to the appropriate LLM based on user preference (GPT-5.2 / GPT-5.4 / Claude Opus / Sonnet / Haiku). The model doesn't pick itself; the harness does.
- **Context-Aware Prompt** — Injects the active skill instructions and the skills registry into the system prompt. This is the harness engineering good context before the model starts reasoning.
- **Inject Context Middleware** — Injects VFS files, plan files, and data files into the model's context window. The harness decides what the model sees.

---

### 3. Agent State — `src/state/`

Models have no durable state beyond their context window. The harness provides state management so the model can track progress across turns and sessions.

- **`todos: list[Todo]`** — The model's task list (id, label, status: pending/in_progress/completed, description). The harness persists this across turns so the model can resume work.
- **`active_skill: str`** — The currently loaded skill instructions. The harness injects this into context so the model operates with domain-specific guidance.
- **`vfs: dict[str, VFile]`** — Virtual File System. The harness provides this mutable workspace so the model can read, write, and share files with sub-agents.
- **`context: AgentContext`** — user_id, user_name, preferred_llm. Harness-managed metadata about the current session.

---

### 4. Skills — `src/skills/` (Progressive Disclosure)

Skills are the harness's solution to context rot. Loading all domain knowledge into the model's context at once degrades performance. Instead, the harness uses progressive disclosure:

- **On startup:** Only skill names and one-line descriptions are loaded (via the Skills Registry at `src/utils/skills_registry.py`). This is lightweight context.
- **On activation:** When the model calls `activate_skill`, the harness loads the full `SKILL.md` instructions into context. The model now has deep domain knowledge without paying the context cost upfront.

**Discovery:** The harness auto-scans `src/skills/*/SKILL.md` for YAML frontmatter (name, description).

**Structure of a Skill Package:**
- `SKILL.md` — Instructions and workflow definitions.
- `assets/` — Templates and section files.
- `references/` — Domain knowledge documents.
- `scripts/` — Diagram generators and utilities.

Skills live on the local filesystem (immutable, read-only). The harness makes them available to the model through tool calls and context injection.

---

### 5. Tools — `src/tools/` (14 Available)

Tools are how the harness gives the model the ability to act on the world. The model outputs a tool call (text); the harness executes it and returns the result. Without tools, the model can only generate text — with them, it can read files, execute code, search, and delegate.

**Cognitive Tools (Harness-Guided Reasoning):**
- `think_tool` — Reflection scratchpad (2–3 sentences, max 40 words). The harness provides this so the model has a structured space for reasoning in the THINK and REFLECT phases.
- `write_todos` — Create/update the task list. The harness enforces one in-progress task at a time.
- `ask_user_input` — Ask the user structured questions (1–3 questions, 2–4 options each). The harness mediates model-to-user communication.
- `activate_skill` — Load a skill's instructions. The harness validates against the registry and injects into state.

**File System Tools (Durable Storage):**
- `read_file` — Paginated reading with offset and limit (default 100 lines).
- `write_file` — Create new files only (cannot overwrite existing — a harness-enforced safety constraint).
- `edit_file` — Targeted modifications using old_string → new_string. Must read first (harness-enforced).
- `delete_file` — Remove files. In VFS, sets content to None to signal deletion.
- `ls_tool` — Directory listing.
- `glob_tool` — Pattern matching with `*`, `**`, `?` wildcards.
- `grep_tool` — Content search with pattern and glob filter.

**Execution Tools (Code Execution & Assembly):**
- `execute_script` — The harness's sandbox for running scripts (Python, etc.). Returns structured JSON (status, message, type, data). Diagram outputs return as png_base64 with diagram IDs. Timeout: 360s (1200s for long tasks). This is the general-purpose tool that lets the model solve problems autonomously by writing and executing code.
- `merge_sections` — Assemble document sections from an ordered path list into a single file. Preserves `{{diagram-id}}` placeholders.

**Delegation Tool (Sub-Agent Spawning):**
- `task` — The harness's orchestration primitive for spawning sub-agents. Parameters: agent_name, description, context_data, output_path. The harness passes VFS to the sub-agent and merges changes back on completion.

---

### 6. Sub Agents — `src/subagents/` (Orchestration Logic)

Sub-agents are themselves **Model + Harness** units — each with their own model, system prompt, tools, and state. The main harness spawns them via the `task` tool to parallelize work and isolate specialized tasks.

**Registry:** `registry.py` auto-registers sub-agents via `register_subagent()`. Each has a `SubAgentConfig` (name, description, system_prompt, tools, model, state_schema). This is harness-level configuration — the model doesn't design its own sub-agents; the harness pre-configures them.

#### Planner (`planner.py`)
- **Purpose:** Create document generation plans from templates.
- **Model:** GPT-5.2 (fixed by harness).
- **Harness Tools:** think, todos, activate_skill, file tools, glob, grep, execute_script.
- **Workflow:** Audit workspace → Activate relevant skill → Read template and extract section index → Classify gaps (Ready / Researchable / Assumption-based / Requires field data) → Write plan to `/<project>/plans/`.
- **Output:** `document_generation_plan.md`.

#### Researcher (`researcher.py`)
- **Purpose:** Web research with sourced summaries. This gives the model access to knowledge beyond its training cutoff.
- **Model:** GPT-5.2 (fixed by harness).
- **Harness Tool:** TavilySearch (max 5 results).
- **Output format:** Executive Summary, Key Findings by theme, Data Points table, Implications, Information Gaps, Sources with URLs.
- **Constraints:** Max 1500 words, superscript citations `^[N]`.

#### Writer (`writer.py`)
- **Purpose:** Write single document sections following templates exactly.
- **Model:** GPT-5.4 (default, set by harness).
- **Harness Tools:** read_file, ls, write_file, edit_file, execute_script.
- **Workflow:** Read section template → Read source data → Generate diagrams → Write section → Embed diagrams as `<img src='{{id}}'>`.
- **Harness-Enforced Rules:** Cannot skip subsections, cannot add unspecified sections, must mark data gaps honestly.

#### General (`general.py`)
- **Purpose:** Complex multi-step tasks (analysis, data processing, workspace organization).
- **Model:** GPT-5.2 (fixed by harness).
- **Harness Tools:** think, todos, activate_skill, file tools, glob, grep, execute_script.
- **Uses the Cognitive Loop:** Think → Plan → Act → Reflect.
- **Harness-Enforced Limitations:** Cannot ask user questions, cannot delegate to other sub-agents.

---

### 7. Dual File Systems (Durable Storage)

The filesystem is the most foundational harness primitive. It gives the model a workspace, enables durable state across sessions, and provides a collaboration surface for multiple agents.

**Local Storage (Immutable)**
- Contains skill templates, references, and scripts.
- Read-only for all agents. The harness enforces immutability.
- Source-of-truth for skill definitions.

**Virtual File System — VFS (Mutable)**
- A `dict[str, VFile]` mapping paths to content.
- The harness provides this as a mutable workspace for project documents, data files, script outputs, and plans.
- Shared between the main agent and all sub-agents — the harness manages VFS passing and merging.
- Changes made by sub-agents are merged back into the main agent's VFS upon task completion.

---

## Data Flow Through the Harness

1. **User → Harness:** User sends a chat message.
2. **Harness (Middleware):** Dynamic Model Selector picks the LLM. Context-Aware Prompt and Inject Context Middleware assemble the context window.
3. **Harness → Model:** The assembled context (system prompt + skills registry + VFS files + user message) is sent to the model.
4. **Model → Harness:** The model outputs text and/or tool calls.
5. **Harness (Tool Execution):** The harness executes tool calls — reads files, runs scripts, searches, or spawns sub-agents.
6. **Harness (Sub-Agent Orchestration):** For delegation, the harness spawns a sub-agent (its own Model + Harness), passes VFS, and merges results back.
7. **Harness → Model:** Tool results are injected back into the model's context. The Cognitive Loop continues.
8. **Harness → User:** When the model signals completion, the harness delivers the final response, documents, and diagrams to the user.

---

## What the Model Does vs. What the Harness Does

| Capability | Model | Harness |
|---|---|---|
| Reasoning and language generation | Yes | — |
| Durable state across turns | — | Yes (state management, VFS) |
| Tool execution | Outputs tool calls | Executes them and returns results |
| Context engineering | — | Yes (middleware, progressive disclosure) |
| Sub-agent orchestration | Decides when to delegate | Spawns, configures, and merges results |
| Enforceable constraints | Follows prompt instructions | Enforces via tool logic (e.g., write_file can't overwrite) |
| Domain knowledge | Via context injection | Skills, references, templates |
| Code execution | Generates code | Runs it in sandbox with timeouts |
| Memory and search | — | VFS, filesystem, TavilySearch |
