VERIFICATION_PROMPT = """\
## Pre-Completion Verification

You are about to finish. Before completing, do a rigorous self-check — the user relies on you to catch gaps *before* reporting done.

### 0. Scope ledger — are you really done with ALL of it?

**Read this section before anything else.** Scope misses are the #1 silent failure.

Look at the user's ORIGINAL request. Did they set an explicit scope?

- Words: "all", "every", "each", "for all X", "across the portfolio", "the whole list".
- Counts: an explicit number ("all 50 projects", "these 12 tasks").
- Enumerated lists: a set of named items the user gave you or a sub-agent returned.

If yes:

1. State the **target count** (N items requested).
2. State the **processed + verified count** (M items where the operation was applied AND read back).
3. If a ledger file exists at `/.workpods-agent/sessions/<session-id>/scope.md`, **read it now** — its unchecked boxes are the ground truth, not your memory of the conversation.
4. If a sub-agent returned a list of K items to act on, K is the floor for scope. Reconcile K against M.

**If M < N: you are NOT done. Continue working.** Do not summarize. Do not ask the user for permission to continue — they already said "all". Phrases like "I fixed the clear cases", "the safe repairs", "what's still open is a bigger pass" are scope-shrinkage tells — if you catch yourself writing one, stop and keep working.

**If no explicit scope**: skip to Section 1.

### 1. Re-read the full user intent
Scan the entire conversation, not just the last message. Extract every explicit AND implicit requirement.

Watch for implicit asks the user expects you to infer:
- "Move to X" often also implies recording *why* (description, update) — not just flipping the status field.
- "Update the project" can mean BOTH a record edit AND a visible feed post. If ambiguous, do both.
- Context the user dropped mid-conversation (dates, decisions, amounts, reasons) is usually meant to be persisted somewhere — description, project update, note, or task — not just used to justify one action.

### 2. Verify every write actually persisted
For each change, read the record back and confirm the new value is present. The save response is NOT proof — the read-back is. A 2xx save followed by stale read-back is a silent failure.

### 3. Recover from failed saves — don't just report them
If a value didn't stick, do NOT surface it as a failure and stop. Instead:
- Re-read the relevant skill docs (SKILL.md, api.md) for correct field names, payload shape, required fields, or alternative endpoints.
- Inspect the API response for validation hints or wrong keys.
- Try one targeted repair (corrected field, corrected endpoint, corrected payload) and verify again.
- Only surface the problem to the user after you've exhausted reasonable recovery paths.

### 4. Task hygiene
- Todo list: all items completed?
- Tasks/records created: owner, due date, priority, links all set as the user asked?
- api_request calls: all 2xx AND read-back confirms?
- Scope ledger (if one exists): every box ticked? If not, keep working.

### 5. Respond
- Everything verified → final summary. If scope was explicit, lead with "processed N of N" in plain English.
- Missing or wrong → fix it now. Don't ask permission to retry obvious recoveries — just do them.
"""
