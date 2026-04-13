# Document Generation Plan Template

This template defines the **structure** of every document generation plan. The planner MUST follow this
format exactly, but the **content is dynamic** — it is derived from the document template being used.

## Key Rule

**Every section and subsection in the document template MUST have a corresponding entry in the plan.**
Do not summarise, group, or skip sections. If the document template has 14 sections, the plan has 14
section blocks. If Section 7 has subsections 7.1–7.7, the plan lists all seven.

---

## How to Use This Template

1. Read the master template (e.g., `solar_pre_feasibility/master.md`).
2. Extract ALL sections, subsections, word count targets, required tables, and diagram specs.
3. For each section, fill in the section block below using workspace data and gap analysis.
4. Do NOT add sections that are not in the document template.
5. Do NOT omit sections that ARE in the document template.

---

## Plan Format — Copy and Adapt

````markdown
# Document Generation Plan

> Review this plan carefully before approving. Generation will not begin until you confirm.

---

## Document Overview

| Field | Value |
|-------|-------|
| **Document** | [Full document title — e.g., Solar Pre-Feasibility Study — Chululu 50kW] |
| **Master Template** | [Template path — e.g., solar-project/assets/solar_pre_feasibility/master.md] |
| **Format** | Markdown |
| **Total Sections** | [N — exact count from the document template] |
| **Language** | [e.g., English / French / Swahili] |
| **Output Folder** | [e.g., /chululu-50kw/sections/] |
| **Final Document Path** | [e.g., /chululu-50kw/chululu_50kw_pre_feasibility_study.md] |

---

## Readiness Summary

| Metric | Count | Sections |
|--------|------:|----------|
| **Ready** (full data available) | [N] | [e.g., 3, 4, 6] |
| **Researchable** (needs web research) | [N] | [e.g., 7, 9, 10] |
| **Assumption-based** (reasonable assumptions) | [N] | [e.g., 5, 8] |
| **Requires field data** (cannot be desk-generated) | [N] | [e.g., 10.2, 13] |

| Prerequisite | Status | Notes |
|--------------|--------|-------|
| Workspace data available | [Ready / Partial / Missing] | [e.g., site_evaluation.json, land_assessment.json found] |
| Skill scripts executed | [All done / Some pending / Not run] | [e.g., demand_modelling not yet run] |
| Template read and parsed | Yes | [Template path] |
| Skill activated | [Yes / No] | [Skill name] |
| Research completed | [Yes / Pending / Not started] | [e.g., 5 topics identified] |

---

## Research Needed

> List each research topic the main agent should launch via researcher subagents.
> If no research is needed, write "None — all sections covered by workspace data."

| # | Topic | Questions to Answer | Covers Sections |
|---|-------|--------------------:|-----------------|
| 1 | [e.g., Regulatory framework] | [e.g., What permits are required for solar IPP in DRC? Grid connection process?] | [e.g., 7.1, 7.2, 7.4] |
| 2 | [e.g., Market and tariff data] | [e.g., Current electricity tariffs in Nord-Kivu? PPA benchmarks for DRC?] | [e.g., 5.4, 9.3] |
| 3 | [e.g., Country energy context] | [e.g., DRC electrification rate? Generation mix? Energy master plan?] | [e.g., 2.1, 5.1] |

---

## Gaps and Risks

### Blocking (cannot proceed without user input)

- [ ] [e.g., Grid connection point not confirmed — which substation should be used? Affects sections 6.5, 7.3]

> If none: "No blocking gaps identified."

### Non-blocking (agent will use assumptions — review and override if needed)

- [ ] [e.g., Land tenure assumed greenfield — basis: industry standard. Confidence: Medium. Affects: 3.3, 8.2]
- [ ] [e.g., No household survey data — Section 5.5 will use modelled estimates. Confidence: Low. Affects: 5.5]

### Sections requiring field data (cannot be desk-generated)

- [e.g., Section 10.2 Community Context — requires actual stakeholder engagement records]
- [e.g., Section 8.2 Social Screening — requires field visit for land use verification]

> These sections will be written with available desk data and clearly marked with
> *"[Data not available — field verification required]"* where primary data is needed.

---

## Section-by-Section Plan

> **EVERY section below comes directly from the document template.**
> **Do not add, skip, reorder, or merge sections.**

---

### Section 1: [Exact title from document template]

| Field | Value |
|-------|-------|
| **Section template** | [e.g., solar-project/assets/solar_pre_feasibility/sections/01_executive_summary.md] |
| **Word count target** | [e.g., 800–1,000 words] |
| **Data readiness** | [Ready / Partial / Needs research / Needs field data] |
| **Data sources** | [List VFS paths — e.g., /chululu-50kw/data/site_evaluation.json, /chululu-50kw/research/combined-research.md] |
| **Output path** | [e.g., /chululu-50kw/sections/01-executive-summary.md] |

**Subsections to cover:**
- [1.1 Subsection title from template — or list bullet points if no subsections]
- [1.2 Subsection title]
- [...]

**Tables required:**
- [e.g., Table ES-1: Project Snapshot — columns: Parameter, Value]
- [e.g., Table ES-2: Financial Snapshot — columns: Metric, Value]
> If none: "None"

**Diagrams required:**
- [e.g., doughnut_chart — CAPEX breakdown by component]
- [e.g., bar_chart — Key financial metrics comparison]
> If none: "None"

**Data mapping:**
- [Which specific data fields/keys from which files map to which subsections]
- [e.g., site_evaluation.json → location, coordinates, elevation for subsection 1.1]
- [e.g., combined-research.md → regulatory overview for subsection 1.3]

**Gaps and assumptions:**
- [e.g., Off-taker credit risk data not available — will use assumption: Medium risk. Confidence: Medium]
> If none: "Fully covered by available data"

**Agent note:**
- [e.g., "Write LAST — after all other sections. Synthesise, do not copy-paste."]
> If none: "Standard writing order"

---

### Section 2: [Exact title from document template]

[Same structure as Section 1 — repeat for EVERY section]

---

### Section 3: [Exact title from document template]

[Same structure as Section 1 — repeat for EVERY section]

---

[... continue for ALL sections from the document template ...]

---

### Section N: [Last section title from document template]

[Same structure as Section 1]

---

## Assumptions Register

| # | Assumption | Based On | Confidence | Affects Sections |
|---|-----------|----------|------------|-----------------|
| 1 | [e.g., Greenfield land access] | [e.g., Industry standard for undeveloped sites] | [High/Medium/Low] | [e.g., 3.3, 8.2] |
| 2 | [e.g., Grid connection at nearest 33kV line] | [e.g., Desktop analysis of grid map] | [Medium] | [e.g., 6.5, 9.1] |
| 3 | [e.g., Module cost at $0.28/Wp] | [e.g., IRENA 2025 benchmark] | [High] | [e.g., 9.1] |

---

## Writing Execution Plan

> How the main agent should orchestrate the writing phase.

### Parallel batch (launch all at once)
| Section | Writer brief summary | Dependencies |
|---------|---------------------|--------------|
| [2] | [e.g., Introduction — project overview, developer profile, study objectives] | None |
| [3] | [e.g., Site Description — geography, topography, land tenure, access] | None |
| [4] | [e.g., Solar Resource — GHI, DNI, temperature, variability] | None |
| [...] | [...] | [...] |

### Sequential (write after parallel batch completes)
| Section | Reason | Depends on |
|---------|--------|-----------|
| [1] | Executive Summary — must synthesise all other sections | All sections |

### Post-writing steps
1. Merge all sections using `merge_sections`
2. Read merged document and verify completeness
3. Check all diagrams are embedded
4. Present to user

---

## Your Approval

> Review this plan — particularly the **Gaps and Risks** section and the **Assumptions Register**.
> Confirm or request changes before generation begins.

**To approve**: Reply "proceed" or select approve when prompted.
**To adjust**: Tell the agent what to change before generation begins.
````

---

## Checklist for the Planner

Before saving the plan, verify:

- [ ] Every section from the document template has a corresponding section block in the plan
- [ ] Section numbers and titles match the document template exactly
- [ ] Word count targets are included for every section
- [ ] All required tables and diagrams are listed per section
- [ ] Data sources are mapped to specific VFS file paths (not generic descriptions)
- [ ] Every section has a clear data readiness status
- [ ] Research topics are listed with specific questions and which sections they cover
- [ ] Assumptions register includes all assumptions with confidence levels
- [ ] Writing execution plan distinguishes parallel vs. sequential sections
- [ ] Executive Summary is marked as "write last"
- [ ] No sections were invented that are not in the document template
- [ ] No sections from the document template were skipped
