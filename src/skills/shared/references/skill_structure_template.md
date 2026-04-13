# Standard SKILL.md Structure

All skills should follow this structure. Common patterns (parameter gathering, work silently, present all results, document generation workflow) live in the system prompt and are guaranteed by the Skill Contract. Skills only contain domain-specific knowledge.

---

```markdown
---
name: <skill-name>
description: "<one-paragraph description for LLM routing>"
---

# <Skill Display Name>

## Reference Files

Load these **only when needed** — do not read them upfront:

| File | When to read |
|------|-------------|
| `references/gotchas.md` | Read before running scripts. Write to it when you discover failure patterns. |
| `examples/commands.md` | Before running scripts — contains example payloads |
| `assets/<document>/master.md` | Only when generating a specific document type — read master template for planning |
| `assets/<document>/sections/*.md` | Individual section templates — passed to writer subagents |

## Scripts

Run via `execute_script` — do NOT read the script source files:
- `scripts/<name>.py` — <purpose>

## Document Types

| Document | Template | Prerequisites |
|----------|----------|---------------|
| `<document_type>` | `assets/<template>/master.md` | <what must complete first> |

## Diagram Types

| Type | When to Use |
|------|-------------|
| `<chart_type>` | <context> |

---

## Workflow

### Step 1: Gather Parameters

<!-- Parameter table ONLY — do NOT restate "ask in ONE question" (system prompt handles that) -->

| Parameter | Description | Required | Example |
|-----------|-------------|----------|---------|
| ... | ... | ... | ... |

**Smart defaults**: <skill-specific silent conversions, e.g., country name to ISO code>

### Step 2-N: <Skill-specific analysis steps>

<!-- What scripts to run, in what order -->
<!-- Do NOT add "work silently" — system prompt guarantees that -->

### Step N+1: Present Results

<!-- Define the PRESENTATION FORMAT only — what sections, what data to show -->
<!-- Do NOT add "present ALL data" — system prompt guarantees that -->

### Step N+2: Document Generation

> **Follow the system prompt's Document Generation Workflow (Steps 0-7).**

**Template mapping:**
| Document | Template path |
|----------|--------------|
| `<type>` | `assets/<template>/master.md` |

**Data source mapping** (which data keys feed which template sections):
| Template Section | Data Source | JSON Path / Key |
|-----------------|-------------|-----------------|
| ... | ... | ... |

**Writer briefing rules** (skill-specific interpretation logic):
- <rule 1>
- <rule 2>

**Skill-specific diagrams:**
- Section N: `<chart_type>` showing <what data>

---

## Domain Knowledge

<!-- Skill-specific technical knowledge that CANNOT live in the system prompt -->
<!-- e.g., scoring frameworks, technology selection logic, country coverage -->

---

## Rules

<!-- ONLY skill-specific rules that ADD to the system prompt -->
<!-- Do NOT include: "work silently", "present ALL results", "ask in ONE question" -->

1. **NEVER** <skill-specific constraint>
2. **ALWAYS** <skill-specific requirement>
```
